from inspect import getdoc
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Security, status
from fastapi_error_map import ErrorAwareRouter, rule

from app.application.commands.publish_survey_template import (
    PublishSurveyTemplateInteractor,
    PublishSurveyTemplateRequest,
    PublishSurveyTemplateResponse,
)
from app.domain.exceptions.survey import SurveyTemplateNotFoundError
from app.infrastructure.exceptions.gateway import DataMapperError
from app.presentation.http.auth.openapi_marker import cookie_scheme
from app.presentation.http.errors.callbacks import log_error, log_info
from app.presentation.http.errors.translators import ServiceUnavailableTranslator


def create_publish_survey_template_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/templates/{template_id}/publish",
        description=getdoc(PublishSurveyTemplateInteractor),
        error_map={
            SurveyTemplateNotFoundError: status.HTTP_404_NOT_FOUND,
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
    async def publish_survey_template(
        template_id: UUID,
        interactor: FromDishka[PublishSurveyTemplateInteractor],
    ) -> PublishSurveyTemplateResponse:
        request_data = PublishSurveyTemplateRequest(template_id=template_id)
        return await interactor.execute(request_data)

    return router
