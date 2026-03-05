from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, TypedDict
from uuid import UUID

from app.application.common.ports.survey_assignment_command_gateway import (
    SurveyAssignmentCommandGateway,
)
from app.application.common.services.current_user import CurrentUserService
from app.domain.exceptions.survey import (
    SurveyAssignmentAssigneePermissionError,
    SurveyAssignmentNotFoundError,
)
from app.domain.value_objects.survey import SurveyAssignmentId
from app.domain.value_objects.user_id import UserId


@dataclass(frozen=True, slots=True, kw_only=True)
class GetMySurveySubmissionQuery:
    assignment_id: UUID


class MySurveySubmissionQM(TypedDict):
    assignment_id: UUID
    assignee_user_id: UUID
    answers: dict[str, Any]
    submitted_at: datetime | None


class GetMySurveySubmissionQueryService:
    """
    - Open to authenticated assignment assignee.
    - Returns the caller's latest submission snapshot.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        survey_assignment_command_gateway: SurveyAssignmentCommandGateway,
    ) -> None:
        self._current_user_service = current_user_service
        self._survey_assignment_command_gateway = survey_assignment_command_gateway

    async def execute(self, query: GetMySurveySubmissionQuery) -> MySurveySubmissionQM:
        current_user = await self._current_user_service.get_current_user()
        assignee_user_id = UserId(current_user.id_.value)
        assignment_id = SurveyAssignmentId(query.assignment_id)

        assignment = await self._survey_assignment_command_gateway.read_by_id(assignment_id)
        if assignment is None:
            raise SurveyAssignmentNotFoundError
        if assignee_user_id not in assignment.assignee_user_ids:
            raise SurveyAssignmentAssigneePermissionError

        submission = await self._survey_assignment_command_gateway.read_submission(
            assignment_id=assignment_id,
            assignee_user_id=assignee_user_id,
        )
        if submission is None:
            return MySurveySubmissionQM(
                assignment_id=assignment_id.value,
                assignee_user_id=assignee_user_id.value,
                answers={},
                submitted_at=None,
            )

        return MySurveySubmissionQM(
            assignment_id=assignment_id.value,
            assignee_user_id=assignee_user_id.value,
            answers=submission.answers,
            submitted_at=submission.submitted_at,
        )
