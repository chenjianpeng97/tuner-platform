from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID
from uuid import uuid4

from app.application.common.ports.flusher import Flusher
from app.application.common.ports.survey_audit_command_gateway import (
    SurveyAuditCommandGateway,
)
from app.application.common.ports.survey_query_gateway import (
    SurveyQueryGateway,
    SurveySubmissionDetailQM,
)
from app.application.common.ports.transaction_manager import (
    TransactionManager,
)
from app.application.common.services.authorization.authorize import authorize
from app.application.common.services.authorization.permissions import (
    CanAccessSurveyLibrary,
    SurveyLibraryContext,
)
from app.application.common.services.current_user import CurrentUserService
from app.domain.exceptions.survey import SurveyAssignmentNotFoundError
from app.domain.entities.survey import SurveyResultAccessAudit
from app.domain.value_objects.survey import (
    SurveyAssignmentId,
    SurveyResultAccessAuditId,
)
from app.domain.value_objects.user_id import UserId


@dataclass(frozen=True, slots=True, kw_only=True)
class GetSurveyAssignmentSubmissionsQuery:
    assignment_id: UUID


class GetSurveyAssignmentSubmissionsQueryService:
    """
    - Open to survey operators.
    - Returns latest effective submission details for an assignment.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        survey_audit_command_gateway: SurveyAuditCommandGateway,
        flusher: Flusher,
        transaction_manager: TransactionManager,
        survey_query_gateway: SurveyQueryGateway,
    ) -> None:
        self._current_user_service = current_user_service
        self._survey_audit_command_gateway = survey_audit_command_gateway
        self._flusher = flusher
        self._transaction_manager = transaction_manager
        self._survey_query_gateway = survey_query_gateway

    async def execute(
        self,
        query: GetSurveyAssignmentSubmissionsQuery,
    ) -> list[SurveySubmissionDetailQM]:
        current_user = await self._current_user_service.get_current_user()
        authorize(
            CanAccessSurveyLibrary(),
            context=SurveyLibraryContext(subject=current_user),
        )
        assignment = await self._survey_query_gateway.read_assignment_by_id(query.assignment_id)
        if assignment is None:
            raise SurveyAssignmentNotFoundError
        results = await self._survey_query_gateway.read_assignment_submissions(
            query.assignment_id
        )
        self._survey_audit_command_gateway.add(
            SurveyResultAccessAudit(
                id_=SurveyResultAccessAuditId(uuid4()),
                actor_user_id=UserId(current_user.id_.value),
                assignment_id=SurveyAssignmentId(query.assignment_id),
                action="survey_result_detail_view",
                occurred_at=datetime.now(UTC),
            )
        )
        await self._flusher.flush()
        await self._transaction_manager.commit()
        return results
