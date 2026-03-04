from inspect import getdoc
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule
from pydantic import BaseModel, ConfigDict

from app.application.commands.update_survey_template import (
    UpdateSurveyTemplateInteractor,
    UpdateSurveyTemplateRequest,
)
from app.domain.entities.survey import SurveyQuestion
from app.domain.enums.survey import QuestionType
from app.domain.exceptions.survey import SurveyTemplateNotFoundError
from app.infrastructure.exceptions.gateway import DataMapperError
from app.presentation.http.auth.openapi_marker import cookie_scheme
from app.presentation.http.errors.callbacks import log_error, log_info
from app.presentation.http.errors.translators import ServiceUnavailableTranslator


class SurveyQuestionPydantic(BaseModel):
    model_config = ConfigDict(frozen=True)

    key: str
    title: str
    question_type: QuestionType
    required: bool
    options: list[str] = []


class UpdateSurveyTemplateRequestPydantic(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    questions: list[SurveyQuestionPydantic]


def create_update_survey_template_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.patch(
        "/templates/{template_id}",
        description=getdoc(UpdateSurveyTemplateInteractor),
        error_map={
            SurveyTemplateNotFoundError: status.HTTP_404_NOT_FOUND,
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
    async def update_survey_template(
        template_id: UUID,
        request_data_pydantic: UpdateSurveyTemplateRequestPydantic,
        interactor: FromDishka[UpdateSurveyTemplateInteractor],
    ) -> None:
        request_data = UpdateSurveyTemplateRequest(
            template_id=template_id,
            name=request_data_pydantic.name,
            questions=[
                SurveyQuestion(
                    key=question.key,
                    title=question.title,
                    question_type=question.question_type,
                    required=question.required,
                    options=tuple(question.options),
                )
                for question in request_data_pydantic.questions
            ],
        )
        await interactor.execute(request_data)

    return router
