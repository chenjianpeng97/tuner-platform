from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest

from app.application.common.exceptions.authorization import AuthorizationError
from app.application.queries.list_survey_audit_logs import (
    ExportSurveyAuditLogsCsvQueryService,
    ListSurveyAuditLogsQuery,
    ListSurveyAuditLogsQueryService,
)
from app.domain.enums.user_role import UserRole


class _AuditQueryGatewayStub:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = [
            {
                "id_": uuid4(),
                "actor_user_id": uuid4(),
                "assignment_id": uuid4(),
                "action": "survey_result_detail_view",
                "occurred_at": datetime.now(UTC),
            }
        ]

    async def read_logs(
        self,
        *,
        from_at: datetime | None,
        to_at: datetime | None,
        limit: int,
        offset: int,
    ) -> list[dict[str, Any]]:
        return self.rows


class _CurrentUserServiceStub:
    def __init__(self, role: UserRole) -> None:
        self._role = role

    async def get_current_user(self) -> Any:
        return SimpleNamespace(role=self._role)


@pytest.mark.asyncio
async def test_list_audit_logs_returns_rows_for_authorized_user() -> None:
    service = ListSurveyAuditLogsQueryService(
        current_user_service=_CurrentUserServiceStub(UserRole.ADMIN),
        survey_audit_query_gateway=_AuditQueryGatewayStub(),
    )

    result = await service.execute(
        ListSurveyAuditLogsQuery(from_at=None, to_at=None, limit=50, offset=0)
    )

    assert len(result) == 1
    assert result[0]["action"] == "survey_result_detail_view"


@pytest.mark.asyncio
async def test_list_audit_logs_raises_forbidden_for_non_admin() -> None:
    service = ListSurveyAuditLogsQueryService(
        current_user_service=_CurrentUserServiceStub(UserRole.USER),
        survey_audit_query_gateway=_AuditQueryGatewayStub(),
    )

    with pytest.raises(AuthorizationError):
        await service.execute(
            ListSurveyAuditLogsQuery(from_at=None, to_at=None, limit=50, offset=0)
        )


@pytest.mark.asyncio
async def test_export_audit_logs_csv_outputs_header_and_rows() -> None:
    list_service = ListSurveyAuditLogsQueryService(
        current_user_service=_CurrentUserServiceStub(UserRole.ADMIN),
        survey_audit_query_gateway=_AuditQueryGatewayStub(),
    )
    export_service = ExportSurveyAuditLogsCsvQueryService(list_service=list_service)

    result = await export_service.execute(
        ListSurveyAuditLogsQuery(from_at=None, to_at=None, limit=50, offset=0)
    )

    assert "id,actor_user_id,assignment_id,action,occurred_at" in result
    assert "survey_result_detail_view" in result
