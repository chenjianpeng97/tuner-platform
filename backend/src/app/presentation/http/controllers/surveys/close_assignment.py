from inspect import getdoc
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from app.application.commands.close_survey_assignment import (
    CloseSurveyAssignmentInteractor,
    CloseSurveyAssignmentRequest,
)
from app.domain.exceptions.survey import SurveyAssignmentNotFoundError
from app.infrastructure.exceptions.gateway import DataMapperError
from app.presentation.http.auth.openapi_marker import cookie_scheme
from app.presentation.http.errors.callbacks import log_error, log_info
from app.presentation.http.errors.translators import ServiceUnavailableTranslator


def create_close_survey_assignment_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/assignments/{assignment_id}/close",
        description=getdoc(CloseSurveyAssignmentInteractor),
        error_map={
            SurveyAssignmentNotFoundError: status.HTTP_404_NOT_FOUND,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Security(cookie_scheme)],
    )
    @inject
    async def close_survey_assignment(
        assignment_id: UUID,
        interactor: FromDishka[CloseSurveyAssignmentInteractor],
    ) -> None:
        request_data = CloseSurveyAssignmentRequest(assignment_id=assignment_id)
        await interactor.execute(request_data)

    return router
