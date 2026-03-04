from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict
from uuid import UUID, uuid4

from app.application.common.ports.flusher import Flusher
from app.application.common.ports.survey_assignment_command_gateway import (
    SurveyAssignmentCommandGateway,
)
from app.application.common.ports.survey_template_command_gateway import (
    SurveyTemplateCommandGateway,
)
from app.application.common.ports.transaction_manager import (
    TransactionManager,
)
from app.domain.entities.survey import SurveyAssignment
from app.domain.exceptions.survey import SurveyTemplateVersionNotFoundError
from app.domain.value_objects.survey import (
    SurveyAssignmentId,
    SurveyTemplateVersionId,
)
from app.domain.value_objects.user_id import UserId


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateSurveyAssignmentRequest:
    template_version_id: UUID
    assignee_user_ids: list[UUID]
    due_at: datetime | None


class CreateSurveyAssignmentResponse(TypedDict):
    id: UUID


class CreateSurveyAssignmentInteractor:
    """
    - Open to survey operators.
    - Creates a survey assignment for a published template version.
    """

    def __init__(
        self,
        survey_assignment_command_gateway: SurveyAssignmentCommandGateway,
        survey_template_command_gateway: SurveyTemplateCommandGateway,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ) -> None:
        self._survey_assignment_command_gateway = survey_assignment_command_gateway
        self._survey_template_command_gateway = survey_template_command_gateway
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def execute(
        self,
        request_data: CreateSurveyAssignmentRequest,
    ) -> CreateSurveyAssignmentResponse:
        template_version = await self._survey_template_command_gateway.read_version_by_id(
            SurveyTemplateVersionId(request_data.template_version_id),
        )
        if template_version is None:
            raise SurveyTemplateVersionNotFoundError

        assignment_id = SurveyAssignmentId(uuid4())
        assignment = SurveyAssignment(
            id_=assignment_id,
            template_version_id=template_version.id_,
            assignee_user_ids=tuple(UserId(user_id) for user_id in request_data.assignee_user_ids),
            due_at=request_data.due_at,
        )
        self._survey_assignment_command_gateway.add(assignment)
        await self._flusher.flush()
        await self._transaction_manager.commit()
        return CreateSurveyAssignmentResponse(id=assignment_id.value)
