from datetime import datetime
from inspect import getdoc
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, Security, status
from fastapi_error_map import ErrorAwareRouter, rule
from pydantic import BaseModel, ConfigDict, Field

from app.application.common.exceptions.authorization import AuthorizationError
from app.application.common.ports.survey_audit_query_gateway import SurveyAuditLogQM
from app.application.queries.list_survey_audit_logs import (
    ListSurveyAuditLogsQuery,
    ListSurveyAuditLogsQueryService,
)
from app.infrastructure.auth.exceptions import AuthenticationError
from app.infrastructure.exceptions.gateway import ReaderError
from app.presentation.http.auth.openapi_marker import cookie_scheme
from app.presentation.http.errors.callbacks import log_error, log_info
from app.presentation.http.errors.translators import ServiceUnavailableTranslator


class ListSurveyAuditLogsRequestPydantic(BaseModel):
    model_config = ConfigDict(frozen=True)

    from_at: datetime | None = None
    to_at: datetime | None = None
    limit: Annotated[int, Field(ge=1, le=500)] = 100
    offset: Annotated[int, Field(ge=0)] = 0


def create_list_survey_audit_logs_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/audit-logs",
        description=getdoc(ListSurveyAuditLogsQueryService),
        error_map={
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
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
    async def list_survey_audit_logs(
        request_data_pydantic: Annotated[ListSurveyAuditLogsRequestPydantic, Depends()],
        interactor: FromDishka[ListSurveyAuditLogsQueryService],
    ) -> list[SurveyAuditLogQM]:
        query = ListSurveyAuditLogsQuery(
            from_at=request_data_pydantic.from_at,
            to_at=request_data_pydantic.to_at,
            limit=request_data_pydantic.limit,
            offset=request_data_pydantic.offset,
        )
        return await interactor.execute(query)

    return router
