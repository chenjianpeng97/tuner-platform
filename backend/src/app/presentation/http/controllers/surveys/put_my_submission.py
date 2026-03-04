from inspect import getdoc
from typing import Any
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule
from pydantic import BaseModel, ConfigDict

from app.application.commands.submit_my_survey_submission import (
    SubmitMySurveySubmissionInteractor,
    SubmitMySurveySubmissionRequest,
)
from app.domain.exceptions.survey import (
    SurveyAssignmentAssigneePermissionError,
    SurveyAssignmentNotFoundError,
    SurveyAssignmentSubmissionNotAllowedError,
)
from app.infrastructure.exceptions.gateway import DataMapperError
from app.presentation.http.auth.openapi_marker import cookie_scheme
from app.presentation.http.errors.callbacks import log_error, log_info
from app.presentation.http.errors.translators import ServiceUnavailableTranslator


class SubmitMySurveySubmissionRequestPydantic(BaseModel):
    model_config = ConfigDict(frozen=True)

    answers: dict[str, Any]


def create_put_my_survey_submission_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.put(
        "/assignments/{assignment_id}/my-submission",
        description=getdoc(SubmitMySurveySubmissionInteractor),
        error_map={
            SurveyAssignmentNotFoundError: status.HTTP_404_NOT_FOUND,
            SurveyAssignmentAssigneePermissionError: status.HTTP_403_FORBIDDEN,
            SurveyAssignmentSubmissionNotAllowedError: status.HTTP_422_UNPROCESSABLE_CONTENT,
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
    async def put_my_survey_submission(
        assignment_id: UUID,
        request_data_pydantic: SubmitMySurveySubmissionRequestPydantic,
        interactor: FromDishka[SubmitMySurveySubmissionInteractor],
    ) -> None:
        request_data = SubmitMySurveySubmissionRequest(
            assignment_id=assignment_id,
            answers=request_data_pydantic.answers,
        )
        await interactor.execute(request_data)

    return router
