from dataclasses import dataclass
from uuid import UUID

from app.application.common.ports.survey_query_gateway import (
    SurveyQueryGateway,
    SurveyTemplateDetailQM,
)
from app.domain.exceptions.survey import SurveyTemplateNotFoundError


@dataclass(frozen=True, slots=True, kw_only=True)
class GetSurveyTemplateQuery:
    template_id: UUID


class GetSurveyTemplateQueryService:
    """
    - Open to survey operators.
    - Returns template draft detail and latest published version reference.
    """

    def __init__(self, survey_query_gateway: SurveyQueryGateway) -> None:
        self._survey_query_gateway = survey_query_gateway

    async def execute(self, query: GetSurveyTemplateQuery) -> SurveyTemplateDetailQM:
        result = await self._survey_query_gateway.read_template_by_id(query.template_id)
        if result is None:
            raise SurveyTemplateNotFoundError
        return result
