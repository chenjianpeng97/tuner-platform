from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from app.application.common.ports.flusher import Flusher
from app.application.common.ports.survey_assignment_command_gateway import (
    SurveyAssignmentCommandGateway,
)
from app.application.common.ports.transaction_manager import (
    TransactionManager,
)
from app.application.common.services.current_user import CurrentUserService
from app.domain.entities.survey import SurveySubmission
from app.domain.exceptions.survey import (
    SurveyAssignmentAssigneePermissionError,
    SurveyAssignmentNotFoundError,
)
from app.domain.value_objects.survey import SurveyAssignmentId, SurveySubmissionId
from app.domain.value_objects.user_id import UserId


@dataclass(frozen=True, slots=True, kw_only=True)
class SubmitMySurveySubmissionRequest:
    assignment_id: UUID
    answers: dict[str, Any]


class SubmitMySurveySubmissionInteractor:
    """
    - Open to authenticated assignment assignee.
    - Saves latest submission snapshot with overwrite semantics.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        survey_assignment_command_gateway: SurveyAssignmentCommandGateway,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ) -> None:
        self._current_user_service = current_user_service
        self._survey_assignment_command_gateway = survey_assignment_command_gateway
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def execute(self, request_data: SubmitMySurveySubmissionRequest) -> None:
        current_user = await self._current_user_service.get_current_user()
        assignee_user_id = UserId(current_user.id_.value)
        assignment_id = SurveyAssignmentId(request_data.assignment_id)

        assignment = await self._survey_assignment_command_gateway.read_by_id(
            assignment_id,
            for_update=True,
        )
        if assignment is None:
            raise SurveyAssignmentNotFoundError
        if assignee_user_id not in assignment.assignee_user_ids:
            raise SurveyAssignmentAssigneePermissionError

        now = datetime.now(UTC)
        assignment.ensure_submission_allowed(now=now)

        submission = await self._survey_assignment_command_gateway.read_submission(
            assignment_id=assignment_id,
            assignee_user_id=assignee_user_id,
            for_update=True,
        )
        is_first_submit = submission is None

        if submission is None:
            submission = SurveySubmission(
                id_=SurveySubmissionId(uuid4()),
                assignment_id=assignment_id,
                assignee_user_id=assignee_user_id,
                answers=request_data.answers,
                submitted_at=now,
            )
        else:
            submission.overwrite(answers=request_data.answers, submitted_at=now)

        await self._survey_assignment_command_gateway.save_submission(submission)

        if is_first_submit:
            assignment.mark_submitted(assignee_user_id)
            await self._survey_assignment_command_gateway.update(assignment)

        await self._flusher.flush()
        await self._transaction_manager.commit()
