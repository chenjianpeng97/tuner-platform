from __future__ import annotations

import json
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import delete, select, update
from sqlalchemy.exc import SQLAlchemyError

from app.application.common.ports.survey_assignment_command_gateway import (
    SurveyAssignmentCommandGateway,
)
from app.domain.entities.survey import SurveyAssignment, SurveySubmission
from app.domain.enums.survey import SurveyAssignmentStatus
from app.domain.value_objects.survey import SurveyAssignmentId, SurveySubmissionId, SurveyTemplateVersionId
from app.domain.value_objects.user_id import UserId
from app.infrastructure.adapters.constants import DB_QUERY_FAILED
from app.infrastructure.adapters.types import MainAsyncSession
from app.infrastructure.exceptions.gateway import DataMapperError
from app.infrastructure.persistence_sqla.mappings.survey import (
    survey_assignment_assignees_table,
    survey_assignments_table,
    survey_submission_answers_table,
    survey_submissions_table,
)
from app.infrastructure.persistence_sqla.models.survey import (
    SurveyAssignmentAssigneeModel,
    SurveyAssignmentModel,
    SurveySubmissionAnswerModel,
    SurveySubmissionModel,
)


class SqlaSurveyAssignmentDataMapper(SurveyAssignmentCommandGateway):
    def __init__(self, session: MainAsyncSession) -> None:
        self._session = session

    def add(self, assignment: SurveyAssignment) -> None:
        """:raises DataMapperError:"""
        try:
            assignment_model = SurveyAssignmentModel()
            assignment_model.id = assignment.id_.value
            assignment_model.template_version_id = assignment.template_version_id.value
            assignment_model.status = assignment.status
            assignment_model.due_at = assignment.due_at
            assignment_model.created_by = None
            assignment_model.created_at = datetime.now(UTC)
            assignment_model.closed_at = None
            self._session.add(assignment_model)

            for assignee_user_id in assignment.assignee_user_ids:
                assignee_model = SurveyAssignmentAssigneeModel()
                assignee_model.id = uuid4()
                assignee_model.assignment_id = assignment.id_.value
                assignee_model.assignment = assignment_model
                assignee_model.assignee_user_id = assignee_user_id.value
                assignee_model.submitted_at = None
                self._session.add(assignee_model)
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err

    async def read_by_id(
        self,
        assignment_id: SurveyAssignmentId,
        for_update: bool = False,
    ) -> SurveyAssignment | None:
        """:raises DataMapperError:"""
        assignment_stmt = select(
            survey_assignments_table.c.id,
            survey_assignments_table.c.template_version_id,
            survey_assignments_table.c.status,
            survey_assignments_table.c.due_at,
        ).where(survey_assignments_table.c.id == assignment_id.value)
        assignee_stmt = select(
            survey_assignment_assignees_table.c.assignee_user_id,
            survey_assignment_assignees_table.c.submitted_at,
        ).where(survey_assignment_assignees_table.c.assignment_id == assignment_id.value)

        if for_update:
            assignment_stmt = assignment_stmt.with_for_update()
            assignee_stmt = assignee_stmt.with_for_update()

        try:
            assignment_row = (await self._session.execute(assignment_stmt)).one_or_none()
            if assignment_row is None:
                return None
            assignee_rows = (await self._session.execute(assignee_stmt)).all()
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err

        assignment = SurveyAssignment(
            id_=SurveyAssignmentId(assignment_row.id),
            template_version_id=SurveyTemplateVersionId(assignment_row.template_version_id),
            assignee_user_ids=tuple(UserId(row.assignee_user_id) for row in assignee_rows),
            due_at=assignment_row.due_at,
        )

        for row in assignee_rows:
            if row.submitted_at is not None:
                assignment.mark_submitted(UserId(row.assignee_user_id))
        if assignment_row.status is SurveyAssignmentStatus.COMPLETED:
            assignment.close()

        return assignment

    async def update(self, assignment: SurveyAssignment) -> None:
        """:raises DataMapperError:"""
        closed_at = datetime.now(UTC) if assignment.status is SurveyAssignmentStatus.COMPLETED else None
        try:
            await self._session.execute(
                update(survey_assignments_table)
                .where(survey_assignments_table.c.id == assignment.id_.value)
                .values(status=assignment.status, closed_at=closed_at)
            )
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err

    async def read_submission(
        self,
        *,
        assignment_id: SurveyAssignmentId,
        assignee_user_id: UserId,
        for_update: bool = False,
    ) -> SurveySubmission | None:
        """:raises DataMapperError:"""
        stmt = select(
            survey_submissions_table.c.id,
            survey_submissions_table.c.submitted_at,
        ).where(
            survey_submissions_table.c.assignment_id == assignment_id.value,
            survey_submissions_table.c.assignee_user_id == assignee_user_id.value,
        )
        if for_update:
            stmt = stmt.with_for_update()

        try:
            row = (await self._session.execute(stmt)).one_or_none()
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err
        if row is None:
            return None

        answers_stmt = (
            select(
                survey_submission_answers_table.c.question_key,
                survey_submission_answers_table.c.answer_value,
            )
            .where(survey_submission_answers_table.c.submission_id == row.id)
            .order_by(survey_submission_answers_table.c.order_no.asc())
        )
        try:
            answer_rows = (await self._session.execute(answers_stmt)).all()
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err

        return SurveySubmission(
            id_=SurveySubmissionId(row.id),
            assignment_id=assignment_id,
            assignee_user_id=assignee_user_id,
            answers={
                answer_row.question_key: json.loads(answer_row.answer_value)
                for answer_row in answer_rows
            },
            submitted_at=row.submitted_at,
        )

    async def save_submission(self, submission: SurveySubmission) -> None:
        """:raises DataMapperError:"""
        existed_stmt = select(survey_submissions_table.c.id).where(
            survey_submissions_table.c.id == submission.id_.value
        )
        submission_model: SurveySubmissionModel | None = None
        try:
            existed = (await self._session.execute(existed_stmt)).one_or_none()
            if existed is None:
                submission_model = SurveySubmissionModel()
                submission_model.id = submission.id_.value
                submission_model.assignment_id = submission.assignment_id.value
                submission_model.assignee_user_id = submission.assignee_user_id.value
                submission_model.submitted_at = submission.submitted_at
                self._session.add(submission_model)
            else:
                await self._session.execute(
                    update(survey_submissions_table)
                    .where(survey_submissions_table.c.id == submission.id_.value)
                    .values(submitted_at=submission.submitted_at)
                )

            await self._session.execute(
                delete(survey_submission_answers_table).where(
                    survey_submission_answers_table.c.submission_id == submission.id_.value,
                )
            )
            for index, (question_key, answer) in enumerate(submission.answers.items()):
                answer_model = SurveySubmissionAnswerModel()
                answer_model.id = uuid4()
                answer_model.submission_id = submission.id_.value
                if submission_model is not None:
                    answer_model.submission = submission_model
                answer_model.question_key = question_key
                answer_model.answer_value = json.dumps(answer)
                answer_model.order_no = index
                self._session.add(answer_model)

            await self._session.execute(
                update(survey_assignment_assignees_table)
                .where(
                    survey_assignment_assignees_table.c.assignment_id
                    == submission.assignment_id.value,
                    survey_assignment_assignees_table.c.assignee_user_id
                    == submission.assignee_user_id.value,
                    survey_assignment_assignees_table.c.submitted_at.is_(None),
                )
                .values(submitted_at=submission.submitted_at)
            )
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err
