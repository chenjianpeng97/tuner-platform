from inspect import getdoc
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from app.application.common.ports.survey_query_gateway import SurveyAssignmentSummaryQM
from app.application.common.exceptions.authorization import AuthorizationError
from app.application.queries.get_survey_assignment_summary import (
    GetSurveyAssignmentSummaryQuery,
    GetSurveyAssignmentSummaryQueryService,
)
from app.domain.exceptions.survey import SurveyAssignmentNotFoundError
from app.infrastructure.auth.exceptions import AuthenticationError
from app.infrastructure.exceptions.gateway import ReaderError
from app.presentation.http.auth.openapi_marker import cookie_scheme
from app.presentation.http.errors.callbacks import log_error, log_info
from app.presentation.http.errors.translators import ServiceUnavailableTranslator


def create_get_survey_assignment_summary_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/assignments/{assignment_id}/summary",
        description=getdoc(GetSurveyAssignmentSummaryQueryService),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            SurveyAssignmentNotFoundError: status.HTTP_404_NOT_FOUND,
            ReaderError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
        },
        default_on_error=log_info,
        status_code=status.HTTP_200_OK,
        dependencies=[Security(cookie_scheme)],
    )
    @inject
    async def get_survey_assignment_summary(
        assignment_id: UUID,
        interactor: FromDishka[GetSurveyAssignmentSummaryQueryService],
    ) -> SurveyAssignmentSummaryQM:
        query = GetSurveyAssignmentSummaryQuery(assignment_id=assignment_id)
        return await interactor.execute(query)

    return router
