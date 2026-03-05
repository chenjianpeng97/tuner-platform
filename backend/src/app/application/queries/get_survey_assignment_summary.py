from dataclasses import dataclass
from uuid import UUID

from app.application.common.ports.survey_query_gateway import (
    SurveyAssignmentSummaryQM,
    SurveyQueryGateway,
)
from app.application.common.services.authorization.authorize import authorize
from app.application.common.services.authorization.permissions import (
    CanAccessSurveyLibrary,
    SurveyLibraryContext,
)
from app.application.common.services.current_user import CurrentUserService
from app.domain.exceptions.survey import SurveyAssignmentNotFoundError


@dataclass(frozen=True, slots=True, kw_only=True)
class GetSurveyAssignmentSummaryQuery:
    assignment_id: UUID


class GetSurveyAssignmentSummaryQueryService:
    """
    - Open to survey operators.
    - Returns aggregated summary data for an assignment.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        survey_query_gateway: SurveyQueryGateway,
    ) -> None:
        self._current_user_service = current_user_service
        self._survey_query_gateway = survey_query_gateway

    async def execute(
        self,
        query: GetSurveyAssignmentSummaryQuery,
    ) -> SurveyAssignmentSummaryQM:
        current_user = await self._current_user_service.get_current_user()
        authorize(
            CanAccessSurveyLibrary(),
            context=SurveyLibraryContext(subject=current_user),
        )
        assignment = await self._survey_query_gateway.read_assignment_by_id(query.assignment_id)
        if assignment is None:
            raise SurveyAssignmentNotFoundError
        return await self._survey_query_gateway.read_assignment_summary(query.assignment_id)
