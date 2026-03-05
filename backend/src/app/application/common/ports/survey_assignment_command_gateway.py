from abc import abstractmethod
from typing import Protocol

from app.domain.entities.survey import SurveyAssignment, SurveySubmission
from app.domain.value_objects.survey import (
    SurveyAssignmentId,
)
from app.domain.value_objects.user_id import UserId


class SurveyAssignmentCommandGateway(Protocol):
    @abstractmethod
    def add(self, assignment: SurveyAssignment) -> None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def read_by_id(
        self,
        assignment_id: SurveyAssignmentId,
        for_update: bool = False,
    ) -> SurveyAssignment | None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def update(self, assignment: SurveyAssignment) -> None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def read_submission(
        self,
        *,
        assignment_id: SurveyAssignmentId,
        assignee_user_id: UserId,
        for_update: bool = False,
    ) -> SurveySubmission | None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def save_submission(self, submission: SurveySubmission) -> None:
        """:raises DataMapperError:"""
