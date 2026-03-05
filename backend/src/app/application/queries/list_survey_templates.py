from app.application.common.ports.survey_query_gateway import (
    SurveyQueryGateway,
    SurveyTemplateListItemQM,
)


class ListSurveyTemplatesQueryService:
    """
    - Open to survey operators.
    - Returns survey template list with latest published version references.
    """

    def __init__(self, survey_query_gateway: SurveyQueryGateway) -> None:
        self._survey_query_gateway = survey_query_gateway

    async def execute(self) -> list[SurveyTemplateListItemQM]:
        return await self._survey_query_gateway.read_templates()
