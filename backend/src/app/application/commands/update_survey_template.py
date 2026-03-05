from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.application.common.ports.flusher import Flusher
from app.application.common.ports.survey_template_command_gateway import (
    SurveyTemplateCommandGateway,
)
from app.application.common.ports.transaction_manager import (
    TransactionManager,
)
from app.domain.entities.survey import SurveyQuestion
from app.domain.exceptions.survey import SurveyTemplateNotFoundError
from app.domain.value_objects.survey import SurveyTemplateId


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateSurveyTemplateRequest:
    template_id: UUID
    name: str
    questions: list[SurveyQuestion]


class UpdateSurveyTemplateInteractor:
    """
    - Open to survey operators.
    - Updates template draft data without mutating published versions.
    """

    def __init__(
        self,
        survey_template_command_gateway: SurveyTemplateCommandGateway,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ) -> None:
        self._survey_template_command_gateway = survey_template_command_gateway
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def execute(self, request_data: UpdateSurveyTemplateRequest) -> None:
        template = await self._survey_template_command_gateway.read_by_id(
            SurveyTemplateId(request_data.template_id),
            for_update=True,
        )
        if template is None:
            raise SurveyTemplateNotFoundError
        template.name = request_data.name
        template.questions = request_data.questions
        await self._survey_template_command_gateway.update(template)
        await self._flusher.flush()
        await self._transaction_manager.commit()
