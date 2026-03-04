from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4
from unittest.mock import AsyncMock

import pytest

from app.application.commands.close_survey_assignment import (
    CloseSurveyAssignmentInteractor,
    CloseSurveyAssignmentRequest,
)
from app.application.commands.create_survey_assignment import (
    CreateSurveyAssignmentInteractor,
    CreateSurveyAssignmentRequest,
)
from app.application.queries.get_survey_assignment import (
    GetSurveyAssignmentQuery,
    GetSurveyAssignmentQueryService,
)
from app.application.queries.list_survey_assignments import (
    ListSurveyAssignmentsQueryService,
)
from app.domain.entities.survey import SurveyAssignment, SurveyQuestion, SurveyTemplateVersion
from app.domain.enums.survey import QuestionType
from app.domain.exceptions.survey import (
    SurveyAssignmentNotFoundError,
    SurveyTemplateVersionNotFoundError,
)
from app.domain.value_objects.survey import (
    SurveyAssignmentId,
    SurveyTemplateId,
    SurveyTemplateVersionId,
)
from app.domain.value_objects.user_id import UserId


class _AssignmentGatewayStub:
    def __init__(self) -> None:
        self.assignment: SurveyAssignment | None = None
        self.added_assignment: SurveyAssignment | None = None
        self.updated_assignment: SurveyAssignment | None = None

    def add(self, assignment: SurveyAssignment) -> None:
        self.added_assignment = assignment

    async def read_by_id(
        self,
        assignment_id: SurveyAssignmentId,
        for_update: bool = False,
    ) -> SurveyAssignment | None:
        return self.assignment

    async def update(self, assignment: SurveyAssignment) -> None:
        self.updated_assignment = assignment

    async def read_submission(self, *, assignment_id: SurveyAssignmentId, assignee_user_id: UserId, for_update: bool = False) -> Any:
        return None

    def save_submission(self, submission: Any) -> None:
        return None


class _TemplateGatewayStub:
    def __init__(self) -> None:
        self.version: SurveyTemplateVersion | None = None

    def add(self, template: Any) -> None:
        return None

    async def read_by_id(self, template_id: Any, for_update: bool = False) -> Any:
        return None

    async def update(self, template: Any) -> None:
        return None

    async def read_version_by_id(
        self,
        version_id: SurveyTemplateVersionId,
        for_update: bool = False,
    ) -> SurveyTemplateVersion | None:
        return self.version

    def save_version(self, template_version: Any) -> None:
        return None

    async def next_published_version_number(self, template_id: Any) -> int:
        return 1


class _QueryGatewayStub:
    def __init__(self) -> None:
        self.assignments: list[dict[str, Any]] = []
        self.assignment_detail: dict[str, Any] | None = None

    async def read_templates(self) -> list[dict[str, Any]]:
        return []

    async def read_template_by_id(self, template_id: UUID) -> dict[str, Any] | None:
        return None

    async def read_assignments(self) -> list[dict[str, Any]]:
        return self.assignments

    async def read_assignment_by_id(self, assignment_id: UUID) -> dict[str, Any] | None:
        return self.assignment_detail

    async def read_assignment_progress(self, assignment_id: UUID) -> dict[str, Any]:
        raise NotImplementedError

    async def read_assignment_submissions(self, assignment_id: UUID) -> list[dict[str, Any]]:
        raise NotImplementedError

    async def read_assignment_summary(self, assignment_id: UUID) -> dict[str, Any]:
        raise NotImplementedError


@pytest.mark.asyncio
async def test_create_assignment_interactor_creates_assignment_and_commits() -> None:
    assignment_gateway = _AssignmentGatewayStub()
    template_gateway = _TemplateGatewayStub()
    template_gateway.version = SurveyTemplateVersion(
        id_=SurveyTemplateVersionId(uuid4()),
        template_id=SurveyTemplateId(uuid4()),
        version=1,
        questions=(
            SurveyQuestion(
                key="q1",
                title="Your role",
                question_type=QuestionType.SINGLE_CHOICE,
                required=True,
                options=("dev", "pm"),
            ),
        ),
    )
    flusher = AsyncMock()
    tx_manager = AsyncMock()

    interactor = CreateSurveyAssignmentInteractor(
        survey_assignment_command_gateway=assignment_gateway,
        survey_template_command_gateway=template_gateway,
        flusher=flusher,
        transaction_manager=tx_manager,
    )

    response = await interactor.execute(
        CreateSurveyAssignmentRequest(
            template_version_id=template_gateway.version.id_.value,
            assignee_user_ids=[uuid4(), uuid4()],
            due_at=datetime.now(UTC),
        )
    )

    assert isinstance(response["id"], UUID)
    assert assignment_gateway.added_assignment is not None
    assert assignment_gateway.added_assignment.assignee_count == 2
    flusher.flush.assert_awaited_once()
    tx_manager.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_assignment_interactor_raises_when_template_version_missing() -> None:
    assignment_gateway = _AssignmentGatewayStub()
    template_gateway = _TemplateGatewayStub()
    flusher = AsyncMock()
    tx_manager = AsyncMock()

    interactor = CreateSurveyAssignmentInteractor(
        survey_assignment_command_gateway=assignment_gateway,
        survey_template_command_gateway=template_gateway,
        flusher=flusher,
        transaction_manager=tx_manager,
    )

    with pytest.raises(SurveyTemplateVersionNotFoundError):
        await interactor.execute(
            CreateSurveyAssignmentRequest(
                template_version_id=uuid4(),
                assignee_user_ids=[uuid4()],
                due_at=None,
            )
        )


@pytest.mark.asyncio
async def test_close_assignment_interactor_marks_completed_and_commits() -> None:
    assignment_gateway = _AssignmentGatewayStub()
    assignment_gateway.assignment = SurveyAssignment(
        id_=SurveyAssignmentId(uuid4()),
        template_version_id=SurveyTemplateVersionId(uuid4()),
        assignee_user_ids=(UserId(uuid4()),),
        due_at=None,
    )
    flusher = AsyncMock()
    tx_manager = AsyncMock()

    interactor = CloseSurveyAssignmentInteractor(
        survey_assignment_command_gateway=assignment_gateway,
        flusher=flusher,
        transaction_manager=tx_manager,
    )

    await interactor.execute(
        CloseSurveyAssignmentRequest(assignment_id=assignment_gateway.assignment.id_.value)
    )

    assert assignment_gateway.updated_assignment is assignment_gateway.assignment
    assert assignment_gateway.assignment.status.value == "completed"
    flusher.flush.assert_awaited_once()
    tx_manager.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_close_assignment_interactor_raises_not_found_when_missing() -> None:
    assignment_gateway = _AssignmentGatewayStub()
    flusher = AsyncMock()
    tx_manager = AsyncMock()

    interactor = CloseSurveyAssignmentInteractor(
        survey_assignment_command_gateway=assignment_gateway,
        flusher=flusher,
        transaction_manager=tx_manager,
    )

    with pytest.raises(SurveyAssignmentNotFoundError):
        await interactor.execute(CloseSurveyAssignmentRequest(assignment_id=uuid4()))


@pytest.mark.asyncio
async def test_list_assignments_query_service_returns_gateway_result() -> None:
    gateway = _QueryGatewayStub()
    gateway.assignments = [
        {
            "id_": uuid4(),
            "template_version_id": uuid4(),
            "status": "in_progress",
            "due_at": None,
            "assignee_count": 2,
            "submitted_count": 1,
            "ratio": 0.5,
        }
    ]
    service = ListSurveyAssignmentsQueryService(survey_query_gateway=gateway)

    result = await service.execute()

    assert result == gateway.assignments


@pytest.mark.asyncio
async def test_get_assignment_query_service_raises_not_found_when_missing() -> None:
    gateway = _QueryGatewayStub()
    service = GetSurveyAssignmentQueryService(survey_query_gateway=gateway)

    with pytest.raises(SurveyAssignmentNotFoundError):
        await service.execute(GetSurveyAssignmentQuery(assignment_id=uuid4()))
