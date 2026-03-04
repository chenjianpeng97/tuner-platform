from dataclasses import dataclass
from uuid import UUID

from app.application.common.ports.survey_query_gateway import (
    SurveyAssignmentDetailQM,
    SurveyQueryGateway,
)
from app.domain.exceptions.survey import SurveyAssignmentNotFoundError


@dataclass(frozen=True, slots=True, kw_only=True)
class GetSurveyAssignmentQuery:
    assignment_id: UUID


class GetSurveyAssignmentQueryService:
    """
    - Open to survey operators.
    - Returns assignment detail with progress fields.
    """

    def __init__(self, survey_query_gateway: SurveyQueryGateway) -> None:
        self._survey_query_gateway = survey_query_gateway

    async def execute(self, query: GetSurveyAssignmentQuery) -> SurveyAssignmentDetailQM:
        result = await self._survey_query_gateway.read_assignment_by_id(query.assignment_id)
        if result is None:
            raise SurveyAssignmentNotFoundError
        return result
