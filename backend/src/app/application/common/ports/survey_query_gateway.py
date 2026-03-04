from abc import abstractmethod
from datetime import datetime
from typing import Any, Protocol, TypedDict
from uuid import UUID

from app.domain.enums.survey import SurveyAssignmentStatus


class AssignmentProgressQM(TypedDict):
    assignment_id: UUID
    assignee_count: int
    submitted_count: int
    ratio: float
    status: SurveyAssignmentStatus


class SurveySubmissionDetailQM(TypedDict):
    assignment_id: UUID
    assignee_user_id: UUID
    answers: dict[str, Any]
    submitted_at: datetime


class SurveyTemplateListItemQM(TypedDict):
    id_: UUID
    name: str
    latest_published_version_id: UUID | None


class SurveyTemplateQuestionQM(TypedDict):
    key: str
    title: str
    question_type: str
    required: bool
    options: list[str]


class SurveyTemplateDetailQM(TypedDict):
    id_: UUID
    name: str
    questions: list[SurveyTemplateQuestionQM]
    latest_published_version_id: UUID | None


class SurveyAssignmentListItemQM(TypedDict):
    id_: UUID
    template_version_id: UUID
    status: SurveyAssignmentStatus
    due_at: datetime | None
    assignee_count: int
    submitted_count: int
    ratio: float


class SurveyAssignmentDetailQM(TypedDict):
    id_: UUID
    template_version_id: UUID
    status: SurveyAssignmentStatus
    due_at: datetime | None
    assignee_user_ids: list[UUID]
    assignee_count: int
    submitted_count: int
    ratio: float


class SurveyAssignmentSummaryQM(TypedDict):
    assignment_id: UUID
    choice_counts: dict[str, dict[str, int]]
    text_answers: dict[str, list[str]]


class SurveyQueryGateway(Protocol):
    @abstractmethod
    async def read_templates(self) -> list[SurveyTemplateListItemQM]:
        """:raises ReaderError:"""

    @abstractmethod
    async def read_template_by_id(
        self,
        template_id: UUID,
    ) -> SurveyTemplateDetailQM | None:
        """:raises ReaderError:"""

    @abstractmethod
    async def read_assignments(self) -> list[SurveyAssignmentListItemQM]:
        """:raises ReaderError:"""

    @abstractmethod
    async def read_assignment_by_id(
        self,
        assignment_id: UUID,
    ) -> SurveyAssignmentDetailQM | None:
        """:raises ReaderError:"""

    @abstractmethod
    async def read_assignment_progress(
        self,
        assignment_id: UUID,
    ) -> AssignmentProgressQM:
        """:raises ReaderError:"""

    @abstractmethod
    async def read_assignment_submissions(
        self,
        assignment_id: UUID,
    ) -> list[SurveySubmissionDetailQM]:
        """:raises ReaderError:"""

    @abstractmethod
    async def read_assignment_summary(
        self,
        assignment_id: UUID,
    ) -> SurveyAssignmentSummaryQM:
        """:raises ReaderError:"""
