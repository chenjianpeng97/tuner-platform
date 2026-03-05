from abc import abstractmethod
from datetime import datetime
from typing import Protocol, TypedDict
from uuid import UUID


class SurveyAuditLogQM(TypedDict):
    id_: UUID
    actor_user_id: UUID
    assignment_id: UUID
    action: str
    occurred_at: datetime


class SurveyAuditQueryGateway(Protocol):
    @abstractmethod
    async def read_logs(
        self,
        *,
        from_at: datetime | None,
        to_at: datetime | None,
        limit: int,
        offset: int,
    ) -> list[SurveyAuditLogQM]:
        """:raises ReaderError:"""
