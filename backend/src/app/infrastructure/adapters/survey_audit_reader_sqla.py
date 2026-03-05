from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.application.common.ports.survey_audit_query_gateway import (
    SurveyAuditLogQM,
    SurveyAuditQueryGateway,
)
from app.infrastructure.adapters.constants import DB_QUERY_FAILED
from app.infrastructure.adapters.types import MainAsyncSession
from app.infrastructure.exceptions.gateway import ReaderError
from app.infrastructure.persistence_sqla.mappings.survey import (
    survey_result_access_audits_table,
)


class SqlaSurveyAuditReader(SurveyAuditQueryGateway):
    def __init__(self, session: MainAsyncSession) -> None:
        self._session = session

    async def read_logs(
        self,
        *,
        from_at: datetime | None,
        to_at: datetime | None,
        limit: int,
        offset: int,
    ) -> list[SurveyAuditLogQM]:
        stmt = select(
            survey_result_access_audits_table.c.id,
            survey_result_access_audits_table.c.actor_user_id,
            survey_result_access_audits_table.c.assignment_id,
            survey_result_access_audits_table.c.action,
            survey_result_access_audits_table.c.occurred_at,
        ).order_by(survey_result_access_audits_table.c.occurred_at.desc())

        if from_at is not None:
            stmt = stmt.where(survey_result_access_audits_table.c.occurred_at >= from_at)
        if to_at is not None:
            stmt = stmt.where(survey_result_access_audits_table.c.occurred_at <= to_at)

        stmt = stmt.limit(limit).offset(offset)

        try:
            rows = (await self._session.execute(stmt)).all()
        except SQLAlchemyError as err:
            raise ReaderError(DB_QUERY_FAILED) from err

        return [
            SurveyAuditLogQM(
                id_=row.id,
                actor_user_id=row.actor_user_id,
                assignment_id=row.assignment_id,
                action=row.action,
                occurred_at=row.occurred_at,
            )
            for row in rows
        ]
