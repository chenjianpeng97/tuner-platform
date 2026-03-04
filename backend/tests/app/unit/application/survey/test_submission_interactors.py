from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any
from uuid import UUID, uuid4
from unittest.mock import AsyncMock

import pytest

from app.application.commands.submit_my_survey_submission import (
    SubmitMySurveySubmissionInteractor,
    SubmitMySurveySubmissionRequest,
)
from app.application.queries.get_my_survey_submission import (
    GetMySurveySubmissionQuery,
    GetMySurveySubmissionQueryService,
)
from app.domain.entities.survey import SurveyAssignment, SurveySubmission
from app.domain.exceptions.survey import (
    SurveyAssignmentAssigneePermissionError,
    SurveyAssignmentSubmissionNotAllowedError,
)
from app.domain.value_objects.survey import (
    SurveyAssignmentId,
    SurveySubmissionId,
    SurveyTemplateVersionId,
)
from app.domain.value_objects.user_id import UserId


class _CurrentUserServiceStub:
    def __init__(self, user_id: UUID) -> None:
        self._user_id = user_id

    async def get_current_user(self) -> Any:
        return SimpleNamespace(id_=SimpleNamespace(value=self._user_id))


class _AssignmentGatewayStub:
    def __init__(self) -> None:
        self.assignment: SurveyAssignment | None = None
        self.submission: SurveySubmission | None = None
        self.saved_submission: SurveySubmission | None = None
        self.updated_assignment_count = 0

    def add(self, assignment: SurveyAssignment) -> None:
        return None

    async def read_by_id(self, assignment_id: SurveyAssignmentId, for_update: bool = False) -> SurveyAssignment | None:
        return self.assignment

    async def update(self, assignment: SurveyAssignment) -> None:
        self.updated_assignment_count += 1

    async def read_submission(
        self,
        *,
        assignment_id: SurveyAssignmentId,
        assignee_user_id: UserId,
        for_update: bool = False,
    ) -> SurveySubmission | None:
        return self.submission

    async def save_submission(self, submission: SurveySubmission) -> None:
        self.saved_submission = submission
        self.submission = submission


@pytest.mark.asyncio
async def test_get_my_submission_returns_empty_snapshot_when_no_submission() -> None:
    assignee_user_id = uuid4()
    gateway = _AssignmentGatewayStub()
    gateway.assignment = SurveyAssignment(
        id_=SurveyAssignmentId(uuid4()),
        template_version_id=SurveyTemplateVersionId(uuid4()),
        assignee_user_ids=(UserId(assignee_user_id),),
        due_at=None,
    )
    service = GetMySurveySubmissionQueryService(
        current_user_service=_CurrentUserServiceStub(assignee_user_id),
        survey_assignment_command_gateway=gateway,
    )

    result = await service.execute(
        GetMySurveySubmissionQuery(assignment_id=gateway.assignment.id_.value)
    )

    assert result["answers"] == {}
    assert result["submitted_at"] is None


@pytest.mark.asyncio
async def test_submit_my_submission_marks_progress_on_first_submit() -> None:
    assignee_user_id = uuid4()
    gateway = _AssignmentGatewayStub()
    gateway.assignment = SurveyAssignment(
        id_=SurveyAssignmentId(uuid4()),
        template_version_id=SurveyTemplateVersionId(uuid4()),
        assignee_user_ids=(UserId(assignee_user_id),),
        due_at=None,
    )
    flusher = AsyncMock()
    tx_manager = AsyncMock()

    interactor = SubmitMySurveySubmissionInteractor(
        current_user_service=_CurrentUserServiceStub(assignee_user_id),
        survey_assignment_command_gateway=gateway,
        flusher=flusher,
        transaction_manager=tx_manager,
    )

    await interactor.execute(
        SubmitMySurveySubmissionRequest(
            assignment_id=gateway.assignment.id_.value,
            answers={"q1": "dev"},
        )
    )

    assert gateway.saved_submission is not None
    assert gateway.saved_submission.answers == {"q1": "dev"}
    assert gateway.updated_assignment_count == 1
    assert gateway.assignment.status.value == "completed"
    flusher.flush.assert_awaited_once()
    tx_manager.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_submit_my_submission_overwrites_without_incrementing_progress() -> None:
    assignee_user_id = uuid4()
    gateway = _AssignmentGatewayStub()
    assignment = SurveyAssignment(
        id_=SurveyAssignmentId(uuid4()),
        template_version_id=SurveyTemplateVersionId(uuid4()),
        assignee_user_ids=(UserId(assignee_user_id), UserId(uuid4())),
        due_at=None,
    )
    assignment.mark_submitted(UserId(assignee_user_id))
    gateway.assignment = assignment
    gateway.submission = SurveySubmission(
        id_=SurveySubmissionId(uuid4()),
        assignment_id=assignment.id_,
        assignee_user_id=UserId(assignee_user_id),
        answers={"q1": "old"},
        submitted_at=datetime.now(UTC),
    )

    interactor = SubmitMySurveySubmissionInteractor(
        current_user_service=_CurrentUserServiceStub(assignee_user_id),
        survey_assignment_command_gateway=gateway,
        flusher=AsyncMock(),
        transaction_manager=AsyncMock(),
    )

    await interactor.execute(
        SubmitMySurveySubmissionRequest(
            assignment_id=assignment.id_.value,
            answers={"q1": "new"},
        )
    )

    assert gateway.saved_submission is not None
    assert gateway.saved_submission.answers == {"q1": "new"}
    assert gateway.updated_assignment_count == 0


@pytest.mark.asyncio
async def test_submit_my_submission_rejects_non_assignee() -> None:
    assignee_user_id = uuid4()
    gateway = _AssignmentGatewayStub()
    gateway.assignment = SurveyAssignment(
        id_=SurveyAssignmentId(uuid4()),
        template_version_id=SurveyTemplateVersionId(uuid4()),
        assignee_user_ids=(UserId(assignee_user_id),),
        due_at=None,
    )

    interactor = SubmitMySurveySubmissionInteractor(
        current_user_service=_CurrentUserServiceStub(uuid4()),
        survey_assignment_command_gateway=gateway,
        flusher=AsyncMock(),
        transaction_manager=AsyncMock(),
    )

    with pytest.raises(SurveyAssignmentAssigneePermissionError):
        await interactor.execute(
            SubmitMySurveySubmissionRequest(
                assignment_id=gateway.assignment.id_.value,
                answers={"q1": "x"},
            )
        )


@pytest.mark.asyncio
async def test_submit_my_submission_rejects_when_assignment_completed() -> None:
    assignee_user_id = uuid4()
    gateway = _AssignmentGatewayStub()
    assignment = SurveyAssignment(
        id_=SurveyAssignmentId(uuid4()),
        template_version_id=SurveyTemplateVersionId(uuid4()),
        assignee_user_ids=(UserId(assignee_user_id), UserId(uuid4())),
        due_at=None,
    )
    assignment.close()
    gateway.assignment = assignment
    interactor = SubmitMySurveySubmissionInteractor(
        current_user_service=_CurrentUserServiceStub(assignee_user_id),
        survey_assignment_command_gateway=gateway,
        flusher=AsyncMock(),
        transaction_manager=AsyncMock(),
    )

    with pytest.raises(SurveyAssignmentSubmissionNotAllowedError):
        await interactor.execute(
            SubmitMySurveySubmissionRequest(
                assignment_id=gateway.assignment.id_.value,
                answers={"q1": "dev"},
            )
        )


@pytest.mark.asyncio
async def test_submit_my_submission_rejects_when_due_date_passed() -> None:
    assignee_user_id = uuid4()
    gateway = _AssignmentGatewayStub()
    gateway.assignment = SurveyAssignment(
        id_=SurveyAssignmentId(uuid4()),
        template_version_id=SurveyTemplateVersionId(uuid4()),
        assignee_user_ids=(UserId(assignee_user_id), UserId(uuid4())),
        due_at=datetime.now(UTC),
    )
    interactor = SubmitMySurveySubmissionInteractor(
        current_user_service=_CurrentUserServiceStub(assignee_user_id),
        survey_assignment_command_gateway=gateway,
        flusher=AsyncMock(),
        transaction_manager=AsyncMock(),
    )

    with pytest.raises(SurveyAssignmentSubmissionNotAllowedError):
        await interactor.execute(
            SubmitMySurveySubmissionRequest(
                assignment_id=gateway.assignment.id_.value,
                answers={"q1": "dev"},
            )
        )
