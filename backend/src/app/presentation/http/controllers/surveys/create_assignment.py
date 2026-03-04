from datetime import datetime
from inspect import getdoc
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule
from pydantic import BaseModel, ConfigDict

from app.application.commands.create_survey_assignment import (
    CreateSurveyAssignmentInteractor,
    CreateSurveyAssignmentRequest,
    CreateSurveyAssignmentResponse,
)
from app.domain.exceptions.survey import SurveyTemplateVersionNotFoundError
from app.infrastructure.exceptions.gateway import DataMapperError
from app.presentation.http.auth.openapi_marker import cookie_scheme
from app.presentation.http.errors.callbacks import log_error, log_info
from app.presentation.http.errors.translators import ServiceUnavailableTranslator


class CreateSurveyAssignmentRequestPydantic(BaseModel):
    model_config = ConfigDict(frozen=True)

    template_version_id: UUID
    assignee_user_ids: list[UUID]
    due_at: datetime | None = None


def create_create_survey_assignment_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/assignments",
        description=getdoc(CreateSurveyAssignmentInteractor),
        error_map={
            SurveyTemplateVersionNotFoundError: status.HTTP_422_UNPROCESSABLE_CONTENT,
            DataMapperError: rule(
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                translator=ServiceUnavailableTranslator(),
                on_error=log_error,
            ),
        },
        default_on_error=log_info,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Security(cookie_scheme)],
    )
    @inject
    async def create_survey_assignment(
        request_data_pydantic: CreateSurveyAssignmentRequestPydantic,
        interactor: FromDishka[CreateSurveyAssignmentInteractor],
    ) -> CreateSurveyAssignmentResponse:
        request_data = CreateSurveyAssignmentRequest(
            template_version_id=request_data_pydantic.template_version_id,
            assignee_user_ids=request_data_pydantic.assignee_user_ids,
            due_at=request_data_pydantic.due_at,
        )
        return await interactor.execute(request_data)

    return router
