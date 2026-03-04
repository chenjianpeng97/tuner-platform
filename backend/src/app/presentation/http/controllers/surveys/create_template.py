from inspect import getdoc

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule
from pydantic import BaseModel, ConfigDict

from app.application.commands.create_survey_template import (
    CreateSurveyTemplateInteractor,
    CreateSurveyTemplateRequest,
    CreateSurveyTemplateResponse,
)
from app.domain.entities.survey import SurveyQuestion
from app.domain.enums.survey import QuestionType
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


class CreateSurveyTemplateRequestPydantic(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    questions: list[SurveyQuestionPydantic]


def create_create_survey_template_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/templates",
        description=getdoc(CreateSurveyTemplateInteractor),
        error_map={
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
    async def create_survey_template(
        request_data_pydantic: CreateSurveyTemplateRequestPydantic,
        interactor: FromDishka[CreateSurveyTemplateInteractor],
    ) -> CreateSurveyTemplateResponse:
        request_data = CreateSurveyTemplateRequest(
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
        return await interactor.execute(request_data)

    return router
