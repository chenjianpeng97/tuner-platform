from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from app.application.common.ports.survey_query_gateway import SurveyAssignmentListItemQM
from app.application.queries.list_survey_assignments import (
    ListSurveyAssignmentsQueryService,
)
from app.infrastructure.exceptions.gateway import ReaderError
from app.presentation.http.auth.openapi_marker import cookie_scheme
from app.presentation.http.errors.callbacks import log_error, log_info
from app.presentation.http.errors.translators import ServiceUnavailableTranslator


def create_list_survey_assignments_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/assignments",
        description=getdoc(ListSurveyAssignmentsQueryService),
        error_map={
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
    async def list_survey_assignments(
        interactor: FromDishka[ListSurveyAssignmentsQueryService],
    ) -> list[SurveyAssignmentListItemQM]:
        return await interactor.execute()

    return router
