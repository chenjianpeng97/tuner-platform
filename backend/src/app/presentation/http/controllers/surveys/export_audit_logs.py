from datetime import datetime
from inspect import getdoc
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, Response, Security, status
from fastapi_error_map import ErrorAwareRouter, rule
from pydantic import BaseModel, ConfigDict

from app.application.common.exceptions.authorization import AuthorizationError
from app.application.queries.list_survey_audit_logs import (
    ExportSurveyAuditLogsCsvQueryService,
    ListSurveyAuditLogsQuery,
)
from app.infrastructure.auth.exceptions import AuthenticationError
from app.infrastructure.exceptions.gateway import ReaderError
from app.presentation.http.auth.openapi_marker import cookie_scheme
from app.presentation.http.errors.callbacks import log_error, log_info
from app.presentation.http.errors.translators import ServiceUnavailableTranslator


class ExportSurveyAuditLogsRequestPydantic(BaseModel):
    model_config = ConfigDict(frozen=True)

    from_at: datetime | None = None
    to_at: datetime | None = None


def create_export_survey_audit_logs_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/audit-logs/export",
        description=getdoc(ExportSurveyAuditLogsCsvQueryService),
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
    async def export_survey_audit_logs(
        request_data_pydantic: Annotated[ExportSurveyAuditLogsRequestPydantic, Depends()],
        interactor: FromDishka[ExportSurveyAuditLogsCsvQueryService],
    ) -> Response:
        query = ListSurveyAuditLogsQuery(
            from_at=request_data_pydantic.from_at,
            to_at=request_data_pydantic.to_at,
            limit=10_000,
            offset=0,
        )
        csv_data = await interactor.execute(query)
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=survey_audit_logs.csv"},
        )

    return router
