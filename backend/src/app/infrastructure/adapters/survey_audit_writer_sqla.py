from sqlalchemy.exc import SQLAlchemyError

from app.application.common.ports.survey_audit_command_gateway import (
    SurveyAuditCommandGateway,
)
from app.domain.entities.survey import SurveyResultAccessAudit
from app.infrastructure.adapters.constants import DB_QUERY_FAILED
from app.infrastructure.adapters.types import MainAsyncSession
from app.infrastructure.exceptions.gateway import DataMapperError
from app.infrastructure.persistence_sqla.models.survey import SurveyResultAccessAuditModel


class SqlaSurveyAuditWriter(SurveyAuditCommandGateway):
    def __init__(self, session: MainAsyncSession) -> None:
        self._session = session

    def add(self, audit_event: SurveyResultAccessAudit) -> None:
        """:raises DataMapperError:"""
        try:
            model = SurveyResultAccessAuditModel()
            model.id = audit_event.id_.value
            model.actor_user_id = audit_event.actor_user_id.value
            model.assignment_id = audit_event.assignment_id.value
            model.action = audit_event.action
            model.occurred_at = audit_event.occurred_at
            self._session.add(model)
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err
