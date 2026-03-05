from app.application.common.ports.survey_query_gateway import (
    SurveyAssignmentListItemQM,
    SurveyQueryGateway,
)


class ListSurveyAssignmentsQueryService:
    """
    - Open to survey operators.
    - Returns assignment list with progress fields.
    """

    def __init__(self, survey_query_gateway: SurveyQueryGateway) -> None:
        self._survey_query_gateway = survey_query_gateway

    async def execute(self) -> list[SurveyAssignmentListItemQM]:
        return await self._survey_query_gateway.read_assignments()
