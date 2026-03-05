from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.application.common.ports.survey_query_gateway import (
    AssignmentProgressQM,
    SurveyAssignmentDetailQM,
    SurveyAssignmentListItemQM,
    SurveyAssignmentSummaryQM,
    SurveyQueryGateway,
    SurveySubmissionDetailQM,
    SurveyTemplateDetailQM,
    SurveyTemplateListItemQM,
    SurveyTemplateQuestionQM,
)
from app.infrastructure.adapters.constants import DB_QUERY_FAILED
from app.infrastructure.adapters.types import MainAsyncSession
from app.infrastructure.exceptions.gateway import ReaderError
from app.infrastructure.persistence_sqla.mappings.survey import (
    survey_assignment_assignees_table,
    survey_assignments_table,
    survey_submission_answers_table,
    survey_submissions_table,
    survey_template_question_options_table,
    survey_template_questions_table,
    survey_template_versions_table,
    survey_templates_table,
)
from app.domain.enums.survey import QuestionType


class SqlaSurveyReader(SurveyQueryGateway):
    def __init__(self, session: MainAsyncSession) -> None:
        self._session = session

    async def read_templates(self) -> list[SurveyTemplateListItemQM]:
        try:
            template_rows = (
                await self._session.execute(
                    select(
                        survey_templates_table.c.id,
                        survey_templates_table.c.name,
                    ).order_by(survey_templates_table.c.created_at.desc())
                )
            ).all()
            result: list[SurveyTemplateListItemQM] = []
            for template_row in template_rows:
                latest_published = (
                    await self._session.execute(
                        select(survey_template_versions_table.c.id)
                        .where(
                            survey_template_versions_table.c.template_id
                            == template_row.id,
                            survey_template_versions_table.c.is_published.is_(True),
                        )
                        .order_by(survey_template_versions_table.c.version.desc())
                        .limit(1)
                    )
                ).one_or_none()
                result.append(
                    SurveyTemplateListItemQM(
                        id_=template_row.id,
                        name=template_row.name,
                        latest_published_version_id=(
                            latest_published.id if latest_published is not None else None
                        ),
                    )
                )
            return result
        except SQLAlchemyError as err:
            raise ReaderError(DB_QUERY_FAILED) from err

    async def read_template_by_id(
        self,
        template_id: UUID,
    ) -> SurveyTemplateDetailQM | None:
        try:
            template_row = (
                await self._session.execute(
                    select(
                        survey_templates_table.c.id,
                        survey_templates_table.c.name,
                    ).where(survey_templates_table.c.id == template_id)
                )
            ).one_or_none()
            if template_row is None:
                return None

            latest_published = (
                await self._session.execute(
                    select(survey_template_versions_table.c.id)
                    .where(
                        survey_template_versions_table.c.template_id == template_id,
                        survey_template_versions_table.c.is_published.is_(True),
                    )
                    .order_by(survey_template_versions_table.c.version.desc())
                    .limit(1)
                )
            ).one_or_none()
            draft_row = (
                await self._session.execute(
                    select(survey_template_versions_table.c.id)
                    .where(
                        survey_template_versions_table.c.template_id == template_id,
                        survey_template_versions_table.c.is_published.is_(False),
                    )
                    .order_by(survey_template_versions_table.c.created_at.desc())
                    .limit(1)
                )
            ).one_or_none()
            questions = await self._read_questions(
                draft_row.id if draft_row is not None else None
            )
        except SQLAlchemyError as err:
            raise ReaderError(DB_QUERY_FAILED) from err

        return SurveyTemplateDetailQM(
            id_=template_row.id,
            name=template_row.name,
            questions=questions,
            latest_published_version_id=(
                latest_published.id if latest_published is not None else None
            ),
        )

    async def read_assignment_progress(
        self,
        assignment_id: UUID,
    ) -> AssignmentProgressQM:
        try:
            assignment_row = (
                await self._session.execute(
                    select(
                        survey_assignments_table.c.id,
                        survey_assignments_table.c.status,
                    ).where(survey_assignments_table.c.id == assignment_id)
                )
            ).one()
            assignee_rows = (
                await self._session.execute(
                    select(survey_assignment_assignees_table.c.submitted_at).where(
                        survey_assignment_assignees_table.c.assignment_id == assignment_id
                    )
                )
            ).all()
        except SQLAlchemyError as err:
            raise ReaderError(DB_QUERY_FAILED) from err

        assignee_count = len(assignee_rows)
        submitted_count = sum(1 for row in assignee_rows if row.submitted_at is not None)
        ratio = (submitted_count / assignee_count) if assignee_count else 0.0
        return AssignmentProgressQM(
            assignment_id=assignment_row.id,
            assignee_count=assignee_count,
            submitted_count=submitted_count,
            ratio=ratio,
            status=assignment_row.status,
        )

    async def read_assignments(self) -> list[SurveyAssignmentListItemQM]:
        try:
            assignment_rows = (
                await self._session.execute(
                    select(
                        survey_assignments_table.c.id,
                        survey_assignments_table.c.template_version_id,
                        survey_assignments_table.c.status,
                        survey_assignments_table.c.due_at,
                        survey_assignments_table.c.created_at,
                    ).order_by(survey_assignments_table.c.created_at.desc())
                )
            ).all()
            assignee_rows = (
                await self._session.execute(
                    select(
                        survey_assignment_assignees_table.c.assignment_id,
                        survey_assignment_assignees_table.c.submitted_at,
                    )
                )
            ).all()
        except SQLAlchemyError as err:
            raise ReaderError(DB_QUERY_FAILED) from err

        progress_by_assignment: dict[UUID, tuple[int, int]] = {}
        for row in assignee_rows:
            assignee_count, submitted_count = progress_by_assignment.get(
                row.assignment_id, (0, 0)
            )
            progress_by_assignment[row.assignment_id] = (
                assignee_count + 1,
                submitted_count + (1 if row.submitted_at is not None else 0),
            )

        result: list[SurveyAssignmentListItemQM] = []
        for row in assignment_rows:
            assignee_count, submitted_count = progress_by_assignment.get(row.id, (0, 0))
            ratio = (submitted_count / assignee_count) if assignee_count else 0.0
            result.append(
                SurveyAssignmentListItemQM(
                    id_=row.id,
                    template_version_id=row.template_version_id,
                    status=row.status,
                    due_at=row.due_at,
                    assignee_count=assignee_count,
                    submitted_count=submitted_count,
                    ratio=ratio,
                )
            )
        return result

    async def read_assignment_by_id(
        self,
        assignment_id: UUID,
    ) -> SurveyAssignmentDetailQM | None:
        try:
            assignment_row = (
                await self._session.execute(
                    select(
                        survey_assignments_table.c.id,
                        survey_assignments_table.c.template_version_id,
                        survey_assignments_table.c.status,
                        survey_assignments_table.c.due_at,
                    ).where(survey_assignments_table.c.id == assignment_id)
                )
            ).one_or_none()
            if assignment_row is None:
                return None
            assignee_rows = (
                await self._session.execute(
                    select(
                        survey_assignment_assignees_table.c.assignee_user_id,
                        survey_assignment_assignees_table.c.submitted_at,
                    ).where(survey_assignment_assignees_table.c.assignment_id == assignment_id)
                )
            ).all()
        except SQLAlchemyError as err:
            raise ReaderError(DB_QUERY_FAILED) from err

        assignee_count = len(assignee_rows)
        submitted_count = sum(1 for row in assignee_rows if row.submitted_at is not None)
        ratio = (submitted_count / assignee_count) if assignee_count else 0.0
        return SurveyAssignmentDetailQM(
            id_=assignment_row.id,
            template_version_id=assignment_row.template_version_id,
            status=assignment_row.status,
            due_at=assignment_row.due_at,
            assignee_user_ids=[row.assignee_user_id for row in assignee_rows],
            assignee_count=assignee_count,
            submitted_count=submitted_count,
            ratio=ratio,
        )

    async def read_assignment_submissions(
        self,
        assignment_id: UUID,
    ) -> list[SurveySubmissionDetailQM]:
        try:
            submission_rows = (
                await self._session.execute(
                    select(
                        survey_submissions_table.c.id,
                        survey_submissions_table.c.assignment_id,
                        survey_submissions_table.c.assignee_user_id,
                        survey_submissions_table.c.submitted_at,
                    )
                    .where(survey_submissions_table.c.assignment_id == assignment_id)
                    .order_by(survey_submissions_table.c.submitted_at.desc())
                )
            ).all()
            if not submission_rows:
                return []
            submission_ids = [row.id for row in submission_rows]
            answer_rows = (
                await self._session.execute(
                    select(
                        survey_submission_answers_table.c.submission_id,
                        survey_submission_answers_table.c.question_key,
                        survey_submission_answers_table.c.answer_value,
                    )
                    .where(
                        survey_submission_answers_table.c.submission_id.in_(
                            submission_ids
                        )
                    )
                    .order_by(survey_submission_answers_table.c.order_no.asc())
                )
            ).all()
        except SQLAlchemyError as err:
            raise ReaderError(DB_QUERY_FAILED) from err

        answers_by_submission: dict[UUID, dict[str, Any]] = {sid: {} for sid in submission_ids}
        for row in answer_rows:
            answers_by_submission[row.submission_id][row.question_key] = json.loads(
                row.answer_value
            )
        return [
            SurveySubmissionDetailQM(
                assignment_id=row.assignment_id,
                assignee_user_id=row.assignee_user_id,
                answers=answers_by_submission[row.id],
                submitted_at=row.submitted_at,
            )
            for row in submission_rows
        ]

    async def read_assignment_summary(
        self,
        assignment_id: UUID,
    ) -> SurveyAssignmentSummaryQM:
        try:
            assignment_row = (
                await self._session.execute(
                    select(survey_assignments_table.c.template_version_id).where(
                        survey_assignments_table.c.id == assignment_id
                    )
                )
            ).one()
            question_rows = (
                await self._session.execute(
                    select(
                        survey_template_questions_table.c.key,
                        survey_template_questions_table.c.question_type,
                    ).where(
                        survey_template_questions_table.c.template_version_id
                        == assignment_row.template_version_id
                    )
                )
            ).all()
            submission_rows = (
                await self._session.execute(
                    select(survey_submissions_table.c.id).where(
                        survey_submissions_table.c.assignment_id == assignment_id
                    )
                )
            ).all()
            submission_ids = [row.id for row in submission_rows]
            answer_rows = (
                await self._session.execute(
                    select(
                        survey_submission_answers_table.c.question_key,
                        survey_submission_answers_table.c.answer_value,
                    ).where(
                        survey_submission_answers_table.c.submission_id.in_(
                            submission_ids
                        )
                    )
                )
            ).all()
        except SQLAlchemyError as err:
            raise ReaderError(DB_QUERY_FAILED) from err

        question_type_by_key = {row.key: row.question_type for row in question_rows}
        choice_counts: dict[str, dict[str, int]] = {}
        text_answers: dict[str, list[str]] = {}

        for row in answer_rows:
            question_type = question_type_by_key.get(row.question_key)
            if question_type is QuestionType.TEXT:
                text_answers.setdefault(row.question_key, []).append(
                    str(json.loads(row.answer_value))
                )
                continue

            if question_type is QuestionType.MULTI_CHOICE:
                values = json.loads(row.answer_value)
                if not isinstance(values, list):
                    values = [values]
                for value in values:
                    choice_counts.setdefault(row.question_key, {})[str(value)] = (
                        choice_counts.setdefault(row.question_key, {}).get(str(value), 0)
                        + 1
                    )
                continue

            value = str(json.loads(row.answer_value))
            choice_counts.setdefault(row.question_key, {})[value] = (
                choice_counts.setdefault(row.question_key, {}).get(value, 0) + 1
            )

        return SurveyAssignmentSummaryQM(
            assignment_id=assignment_id,
            choice_counts=choice_counts,
            text_answers=text_answers,
        )

    async def _read_questions(
        self,
        template_version_id: UUID | None,
    ) -> list[SurveyTemplateQuestionQM]:
        if template_version_id is None:
            return []
        question_rows = (
            await self._session.execute(
                select(
                    survey_template_questions_table.c.id,
                    survey_template_questions_table.c.key,
                    survey_template_questions_table.c.title,
                    survey_template_questions_table.c.question_type,
                    survey_template_questions_table.c.required,
                    survey_template_questions_table.c.order_no,
                )
                .where(
                    survey_template_questions_table.c.template_version_id
                    == template_version_id,
                )
                .order_by(survey_template_questions_table.c.order_no.asc())
            )
        ).all()
        if not question_rows:
            return []

        question_ids = [row.id for row in question_rows]
        option_rows = (
            await self._session.execute(
                select(
                    survey_template_question_options_table.c.question_id,
                    survey_template_question_options_table.c.value,
                )
                .where(survey_template_question_options_table.c.question_id.in_(question_ids))
                .order_by(survey_template_question_options_table.c.order_no.asc())
            )
        ).all()
        options_by_question: dict[UUID, list[str]] = {qid: [] for qid in question_ids}
        for option_row in option_rows:
            options_by_question[option_row.question_id].append(option_row.value)

        return [
            SurveyTemplateQuestionQM(
                key=row.key,
                title=row.title,
                question_type=str(row.question_type.value),
                required=bool(row.required),
                options=options_by_question[row.id],
            )
            for row in question_rows
        ]
