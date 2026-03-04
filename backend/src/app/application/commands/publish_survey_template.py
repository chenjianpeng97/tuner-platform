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
from app.domain.exceptions.survey import SurveyTemplateNotFoundError
from app.domain.value_objects.survey import (
    SurveyTemplateId,
    SurveyTemplateVersionId,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PublishSurveyTemplateRequest:
    template_id: UUID


class PublishSurveyTemplateResponse(TypedDict):
    version_id: UUID


class PublishSurveyTemplateInteractor:
    """
    - Open to survey operators.
    - Creates an immutable published version from current template draft.
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
        request_data: PublishSurveyTemplateRequest,
    ) -> PublishSurveyTemplateResponse:
        template_id = SurveyTemplateId(request_data.template_id)
        template = await self._survey_template_command_gateway.read_by_id(
            template_id,
            for_update=True,
        )
        if template is None:
            raise SurveyTemplateNotFoundError
        next_version = await self._survey_template_command_gateway.next_published_version_number(
            template_id
        )
        version_id = SurveyTemplateVersionId(uuid4())
        template_version = template.publish(version_id=version_id, version=next_version)
        self._survey_template_command_gateway.save_version(template_version)
        await self._flusher.flush()
        await self._transaction_manager.commit()
        return PublishSurveyTemplateResponse(version_id=version_id.value)
