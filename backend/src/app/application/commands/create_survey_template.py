from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID, uuid4

from app.application.common.ports.flusher import Flusher
from app.application.common.ports.survey_template_command_gateway import (
    SurveyTemplateCommandGateway,
)
from app.application.common.ports.transaction_manager import (
    TransactionManager,
)
from app.domain.entities.survey import SurveyQuestion, SurveyTemplate
from app.domain.value_objects.survey import SurveyTemplateId


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateSurveyTemplateRequest:
    name: str
    questions: list[SurveyQuestion]


class CreateSurveyTemplateResponse(TypedDict):
    id: UUID


class CreateSurveyTemplateInteractor:
    """
    - Open to survey operators.
    - Creates a survey template with draft questions.
    - Published versions are created by a dedicated publish operation.
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

    async def execute(
        self,
        request_data: CreateSurveyTemplateRequest,
    ) -> CreateSurveyTemplateResponse:
        template_id = SurveyTemplateId(uuid4())
        template = SurveyTemplate(
            id_=template_id,
            name=request_data.name,
            questions=request_data.questions,
        )
        self._survey_template_command_gateway.add(template)
        await self._flusher.flush()
        await self._transaction_manager.commit()
        return CreateSurveyTemplateResponse(id=template_id.value)
