from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from io import StringIO

from app.application.common.ports.survey_audit_query_gateway import (
    SurveyAuditLogQM,
    SurveyAuditQueryGateway,
)
from app.application.common.services.authorization.authorize import authorize
from app.application.common.services.authorization.permissions import (
    CanAccessSurveyLibrary,
    SurveyLibraryContext,
)
from app.application.common.services.current_user import CurrentUserService


@dataclass(frozen=True, slots=True, kw_only=True)
class ListSurveyAuditLogsQuery:
    from_at: datetime | None
    to_at: datetime | None
    limit: int = 100
    offset: int = 0


class ListSurveyAuditLogsQueryService:
    """
    - Open to authorized survey auditors.
    - Returns survey result access audit logs.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        survey_audit_query_gateway: SurveyAuditQueryGateway,
    ) -> None:
        self._current_user_service = current_user_service
        self._survey_audit_query_gateway = survey_audit_query_gateway

    async def execute(self, query: ListSurveyAuditLogsQuery) -> list[SurveyAuditLogQM]:
        current_user = await self._current_user_service.get_current_user()
        authorize(
            CanAccessSurveyLibrary(),
            context=SurveyLibraryContext(subject=current_user),
        )
        return await self._survey_audit_query_gateway.read_logs(
            from_at=query.from_at,
            to_at=query.to_at,
            limit=query.limit,
            offset=query.offset,
        )


class ExportSurveyAuditLogsCsvQueryService:
    """
    - Open to authorized survey auditors.
    - Exports survey result access audit logs as CSV.
    """

    def __init__(
        self,
        list_service: ListSurveyAuditLogsQueryService,
    ) -> None:
        self._list_service = list_service

    async def execute(self, query: ListSurveyAuditLogsQuery) -> str:
        rows = await self._list_service.execute(query)
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["id", "actor_user_id", "assignment_id", "action", "occurred_at"])
        for row in rows:
            writer.writerow(
                [
                    str(row["id_"]),
                    str(row["actor_user_id"]),
                    str(row["assignment_id"]),
                    row["action"],
                    row["occurred_at"].isoformat(),
                ]
            )
        return buffer.getvalue()
