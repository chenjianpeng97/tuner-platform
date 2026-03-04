from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.domain.entities.survey import (
    SurveyAssignment,
    SurveyQuestion,
    SurveySubmission,
    SurveyTemplate,
)
from app.domain.enums.survey import (
    QuestionType,
    SurveyAssignmentStatus,
)
from app.domain.exceptions.survey import SurveyAssignmentSubmissionNotAllowedError
from app.domain.value_objects.survey import (
    SurveyAssignmentId,
    SurveySubmissionId,
    SurveyTemplateId,
    SurveyTemplateVersionId,
)
from app.domain.value_objects.user_id import UserId


def _sample_questions() -> list[SurveyQuestion]:
    return [
        SurveyQuestion(
            key="q1",
            title="Your role?",
            question_type=QuestionType.SINGLE_CHOICE,
            required=True,
            options=("dev", "pm"),
        ),
        SurveyQuestion(
            key="q2",
            title="Features used",
            question_type=QuestionType.MULTI_CHOICE,
            required=True,
            options=("dashboard", "api"),
        ),
        SurveyQuestion(
            key="q3",
            title="Additional feedback",
            question_type=QuestionType.TEXT,
            required=False,
            options=(),
        ),
    ]


def test_published_template_version_is_frozen() -> None:
    template = SurveyTemplate(
        id_=SurveyTemplateId(uuid4()),
        name="Platform Feedback",
        questions=_sample_questions(),
    )
    version_id = SurveyTemplateVersionId(uuid4())

    version = template.publish(version_id=version_id, version=1)
    template.questions[0] = SurveyQuestion(
        key="q1",
        title="Mutated in draft",
        question_type=QuestionType.SINGLE_CHOICE,
        required=True,
        options=("dev", "pm"),
    )

    assert version.id_ == version_id
    assert version.template_id == template.id_
    assert version.version == 1
    assert version.questions[0].title == "Your role?"


def test_assignment_auto_completes_when_all_assignees_submitted() -> None:
    assignee_1 = UserId(uuid4())
    assignee_2 = UserId(uuid4())

    assignment = SurveyAssignment(
        id_=SurveyAssignmentId(uuid4()),
        template_version_id=SurveyTemplateVersionId(uuid4()),
        assignee_user_ids=(assignee_1, assignee_2),
        due_at=None,
    )

    assignment.mark_submitted(assignee_1)
    assert assignment.status is SurveyAssignmentStatus.IN_PROGRESS
    assert assignment.submitted_count == 1
    assert assignment.assignee_count == 2

    assignment.mark_submitted(assignee_2)
    assert assignment.status is SurveyAssignmentStatus.COMPLETED
    assert assignment.submitted_count == 2


def test_assignment_can_be_closed_manually() -> None:
    assignment = SurveyAssignment(
        id_=SurveyAssignmentId(uuid4()),
        template_version_id=SurveyTemplateVersionId(uuid4()),
        assignee_user_ids=(UserId(uuid4()),),
        due_at=None,
    )

    assignment.close()
    assert assignment.status is SurveyAssignmentStatus.COMPLETED


def test_submission_not_allowed_after_due_date() -> None:
    now = datetime.now(UTC)
    assignee = UserId(uuid4())
    assignment = SurveyAssignment(
        id_=SurveyAssignmentId(uuid4()),
        template_version_id=SurveyTemplateVersionId(uuid4()),
        assignee_user_ids=(assignee,),
        due_at=now - timedelta(seconds=1),
    )

    with pytest.raises(SurveyAssignmentSubmissionNotAllowedError):
        assignment.ensure_submission_allowed(now=now)


def test_submission_not_allowed_when_assignment_completed() -> None:
    now = datetime.now(UTC)
    assignee = UserId(uuid4())
    assignment = SurveyAssignment(
        id_=SurveyAssignmentId(uuid4()),
        template_version_id=SurveyTemplateVersionId(uuid4()),
        assignee_user_ids=(assignee,),
        due_at=None,
    )
    assignment.close()

    with pytest.raises(SurveyAssignmentSubmissionNotAllowedError):
        assignment.ensure_submission_allowed(now=now)


def test_latest_submission_overwrites_previous_answers() -> None:
    assignee = UserId(uuid4())
    submission = SurveySubmission(
        id_=SurveySubmissionId(uuid4()),
        assignment_id=SurveyAssignmentId(uuid4()),
        assignee_user_id=assignee,
        answers={"q1": "dev"},
        submitted_at=datetime.now(UTC),
    )
    now = datetime.now(UTC) + timedelta(minutes=1)

    submission.overwrite(answers={"q1": "pm", "q3": "nice"}, submitted_at=now)

    assert submission.answers == {"q1": "pm", "q3": "nice"}
    assert submission.submitted_at == now
