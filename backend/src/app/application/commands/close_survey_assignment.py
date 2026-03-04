from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.application.common.ports.flusher import Flusher
from app.application.common.ports.survey_assignment_command_gateway import (
    SurveyAssignmentCommandGateway,
)
from app.application.common.ports.transaction_manager import (
    TransactionManager,
)
from app.domain.exceptions.survey import SurveyAssignmentNotFoundError
from app.domain.value_objects.survey import SurveyAssignmentId


@dataclass(frozen=True, slots=True, kw_only=True)
class CloseSurveyAssignmentRequest:
    assignment_id: UUID


class CloseSurveyAssignmentInteractor:
    """
    - Open to survey operators.
    - Closes an in-progress assignment and marks it completed.
    """

    def __init__(
        self,
        survey_assignment_command_gateway: SurveyAssignmentCommandGateway,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ) -> None:
        self._survey_assignment_command_gateway = survey_assignment_command_gateway
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def execute(self, request_data: CloseSurveyAssignmentRequest) -> None:
        assignment = await self._survey_assignment_command_gateway.read_by_id(
            SurveyAssignmentId(request_data.assignment_id),
            for_update=True,
        )
        if assignment is None:
            raise SurveyAssignmentNotFoundError

        assignment.close()
        await self._survey_assignment_command_gateway.update(assignment)
        await self._flusher.flush()
        await self._transaction_manager.commit()
