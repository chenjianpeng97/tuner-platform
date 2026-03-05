from abc import abstractmethod
from typing import Protocol

from app.domain.entities.survey import SurveyResultAccessAudit


class SurveyAuditCommandGateway(Protocol):
    @abstractmethod
    def add(self, audit_event: SurveyResultAccessAudit) -> None:
        """:raises DataMapperError:"""
