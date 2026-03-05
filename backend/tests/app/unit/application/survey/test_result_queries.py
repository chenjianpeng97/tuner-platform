from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from uuid import UUID, uuid4
from unittest.mock import AsyncMock

import pytest

from app.application.common.exceptions.authorization import AuthorizationError
from app.application.queries.get_survey_assignment_submissions import (
    GetSurveyAssignmentSubmissionsQuery,
    GetSurveyAssignmentSubmissionsQueryService,
)
from app.application.queries.get_survey_assignment_summary import (
    GetSurveyAssignmentSummaryQuery,
    GetSurveyAssignmentSummaryQueryService,
)
from app.domain.enums.user_role import UserRole
from app.domain.exceptions.survey import SurveyAssignmentNotFoundError


class _QueryGatewayStub:
    def __init__(self) -> None:
        self.assignment: dict[str, Any] | None = None
        self.submissions: list[dict[str, Any]] = []
        self.summary: dict[str, Any] = {
            "assignment_id": uuid4(),
            "choice_counts": {},
            "text_answers": {},
        }

    async def read_templates(self) -> list[dict[str, Any]]:
        return []

    async def read_template_by_id(self, template_id: UUID) -> dict[str, Any] | None:
        return None

    async def read_assignments(self) -> list[dict[str, Any]]:
        return []

    async def read_assignment_by_id(self, assignment_id: UUID) -> dict[str, Any] | None:
        return self.assignment

    async def read_assignment_progress(self, assignment_id: UUID) -> dict[str, Any]:
        raise NotImplementedError

    async def read_assignment_submissions(self, assignment_id: UUID) -> list[dict[str, Any]]:
        return self.submissions

    async def read_assignment_summary(self, assignment_id: UUID) -> dict[str, Any]:
        return self.summary


class _CurrentUserServiceStub:
    def __init__(self, role: UserRole) -> None:
        self._role = role
        self._user_id = uuid4()

    async def get_current_user(self) -> Any:
        return SimpleNamespace(role=self._role, id_=SimpleNamespace(value=self._user_id))


class _AuditGatewayStub:
    def __init__(self) -> None:
        self.events: list[Any] = []

    def add(self, audit_event: Any) -> None:
        self.events.append(audit_event)


@pytest.mark.asyncio
async def test_get_assignment_submissions_returns_gateway_data() -> None:
    gateway = _QueryGatewayStub()
    assignment_id = uuid4()
    gateway.assignment = {
        "id_": assignment_id,
        "template_version_id": uuid4(),
        "status": "in_progress",
        "due_at": None,
        "assignee_user_ids": [],
        "assignee_count": 2,
        "submitted_count": 1,
        "ratio": 0.5,
    }
    gateway.submissions = [
        {
            "assignment_id": assignment_id,
            "assignee_user_id": uuid4(),
            "answers": {"q1": "dev"},
            "submitted_at": None,
        }
    ]

    service = GetSurveyAssignmentSubmissionsQueryService(
        current_user_service=_CurrentUserServiceStub(UserRole.ADMIN),
        survey_audit_command_gateway=_AuditGatewayStub(),
        flusher=AsyncMock(),
        transaction_manager=AsyncMock(),
        survey_query_gateway=gateway,
    )

    result = await service.execute(
        GetSurveyAssignmentSubmissionsQuery(assignment_id=assignment_id)
    )

    assert result == gateway.submissions


@pytest.mark.asyncio
async def test_get_assignment_submissions_raises_when_assignment_missing() -> None:
    gateway = _QueryGatewayStub()
    service = GetSurveyAssignmentSubmissionsQueryService(
        current_user_service=_CurrentUserServiceStub(UserRole.ADMIN),
        survey_audit_command_gateway=_AuditGatewayStub(),
        flusher=AsyncMock(),
        transaction_manager=AsyncMock(),
        survey_query_gateway=gateway,
    )

    with pytest.raises(SurveyAssignmentNotFoundError):
        await service.execute(GetSurveyAssignmentSubmissionsQuery(assignment_id=uuid4()))


@pytest.mark.asyncio
async def test_get_assignment_summary_returns_gateway_data() -> None:
    gateway = _QueryGatewayStub()
    assignment_id = uuid4()
    gateway.assignment = {
        "id_": assignment_id,
        "template_version_id": uuid4(),
        "status": "in_progress",
        "due_at": None,
        "assignee_user_ids": [],
        "assignee_count": 2,
        "submitted_count": 1,
        "ratio": 0.5,
    }

    service = GetSurveyAssignmentSummaryQueryService(
        current_user_service=_CurrentUserServiceStub(UserRole.ADMIN),
        survey_query_gateway=gateway,
    )

    result = await service.execute(GetSurveyAssignmentSummaryQuery(assignment_id=assignment_id))

    assert result == gateway.summary


@pytest.mark.asyncio
async def test_get_assignment_summary_raises_when_assignment_missing() -> None:
    gateway = _QueryGatewayStub()
    service = GetSurveyAssignmentSummaryQueryService(
        current_user_service=_CurrentUserServiceStub(UserRole.ADMIN),
        survey_query_gateway=gateway,
    )

    with pytest.raises(SurveyAssignmentNotFoundError):
        await service.execute(GetSurveyAssignmentSummaryQuery(assignment_id=uuid4()))


@pytest.mark.asyncio
async def test_get_assignment_summary_raises_forbidden_when_user_lacks_permission() -> None:
    gateway = _QueryGatewayStub()
    service = GetSurveyAssignmentSummaryQueryService(
        current_user_service=_CurrentUserServiceStub(UserRole.USER),
        survey_query_gateway=gateway,
    )

    with pytest.raises(AuthorizationError):
        await service.execute(GetSurveyAssignmentSummaryQuery(assignment_id=uuid4()))


@pytest.mark.asyncio
async def test_get_assignment_submissions_writes_audit_event() -> None:
    gateway = _QueryGatewayStub()
    assignment_id = uuid4()
    gateway.assignment = {
        "id_": assignment_id,
        "template_version_id": uuid4(),
        "status": "in_progress",
        "due_at": None,
        "assignee_user_ids": [],
        "assignee_count": 1,
        "submitted_count": 1,
        "ratio": 1.0,
    }
    audit_gateway = _AuditGatewayStub()
    flusher = AsyncMock()
    tx_manager = AsyncMock()
    service = GetSurveyAssignmentSubmissionsQueryService(
        current_user_service=_CurrentUserServiceStub(UserRole.ADMIN),
        survey_audit_command_gateway=audit_gateway,
        flusher=flusher,
        transaction_manager=tx_manager,
        survey_query_gateway=gateway,
    )

    await service.execute(GetSurveyAssignmentSubmissionsQuery(assignment_id=assignment_id))

    assert len(audit_gateway.events) == 1
    assert audit_gateway.events[0].assignment_id.value == assignment_id
    assert audit_gateway.events[0].action == "survey_result_detail_view"
    flusher.flush.assert_awaited_once()
    tx_manager.commit.assert_awaited_once()
