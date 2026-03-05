from inspect import getdoc
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from app.application.queries.get_my_survey_submission import (
    GetMySurveySubmissionQuery,
    GetMySurveySubmissionQueryService,
    MySurveySubmissionQM,
)
from app.domain.exceptions.survey import (
    SurveyAssignmentAssigneePermissionError,
    SurveyAssignmentNotFoundError,
)
from app.infrastructure.exceptions.gateway import DataMapperError
from app.presentation.http.auth.openapi_marker import cookie_scheme
from app.presentation.http.errors.callbacks import log_error, log_info
from app.presentation.http.errors.translators import ServiceUnavailableTranslator


def create_get_my_survey_submission_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/assignments/{assignment_id}/my-submission",
        description=getdoc(GetMySurveySubmissionQueryService),
        error_map={
            SurveyAssignmentNotFoundError: status.HTTP_404_NOT_FOUND,
            SurveyAssignmentAssigneePermissionError: status.HTTP_403_FORBIDDEN,
            DataMapperError: rule(
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
    async def get_my_survey_submission(
        assignment_id: UUID,
        interactor: FromDishka[GetMySurveySubmissionQueryService],
    ) -> MySurveySubmissionQM:
        query = GetMySurveySubmissionQuery(assignment_id=assignment_id)
        return await interactor.execute(query)

    return router
