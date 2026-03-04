from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.domain.entities.base import Entity
from app.domain.enums.survey import QuestionType, SurveyAssignmentStatus
from app.domain.exceptions.survey import SurveyAssignmentSubmissionNotAllowedError
from app.domain.value_objects.survey import (
    SurveyAssignmentId,
    SurveyResultAccessAuditId,
    SurveySubmissionId,
    SurveyTemplateId,
    SurveyTemplateVersionId,
)
from app.domain.value_objects.user_id import UserId


@dataclass(frozen=True, slots=True)
class SurveyQuestion:
    key: str
    title: str
    question_type: QuestionType
    required: bool
    options: tuple[str, ...]


class SurveyTemplate(Entity[SurveyTemplateId]):
    def __init__(
        self,
        *,
        id_: SurveyTemplateId,
        name: str,
        questions: list[SurveyQuestion],
    ) -> None:
        super().__init__(id_=id_)
        self.name = name
        self.questions = questions

    def publish(
        self,
        *,
        version_id: SurveyTemplateVersionId,
        version: int,
    ) -> SurveyTemplateVersion:
        # Freeze question snapshot at publish time.
        return SurveyTemplateVersion(
            id_=version_id,
            template_id=self.id_,
            version=version,
            questions=tuple(self.questions),
        )


class SurveyTemplateVersion(Entity[SurveyTemplateVersionId]):
    def __init__(
        self,
        *,
        id_: SurveyTemplateVersionId,
        template_id: SurveyTemplateId,
        version: int,
        questions: tuple[SurveyQuestion, ...],
    ) -> None:
        super().__init__(id_=id_)
        self.template_id = template_id
        self.version = version
        self.questions = questions


class SurveyAssignment(Entity[SurveyAssignmentId]):
    def __init__(
        self,
        *,
        id_: SurveyAssignmentId,
        template_version_id: SurveyTemplateVersionId,
        assignee_user_ids: tuple[UserId, ...],
        due_at: datetime | None,
    ) -> None:
        super().__init__(id_=id_)
        self.template_version_id = template_version_id
        self.assignee_user_ids = assignee_user_ids
        self.due_at = due_at
        self.status = SurveyAssignmentStatus.IN_PROGRESS
        self._submitted_user_ids: set[UserId] = set()

    @property
    def assignee_count(self) -> int:
        return len(self.assignee_user_ids)

    @property
    def submitted_count(self) -> int:
        return len(self._submitted_user_ids)

    def mark_submitted(self, user_id: UserId) -> None:
        self._submitted_user_ids.add(user_id)
        if self.submitted_count == self.assignee_count:
            self.status = SurveyAssignmentStatus.COMPLETED

    def close(self) -> None:
        self.status = SurveyAssignmentStatus.COMPLETED

    def ensure_submission_allowed(self, *, now: datetime) -> None:
        if self.status is SurveyAssignmentStatus.COMPLETED:
            raise SurveyAssignmentSubmissionNotAllowedError(reason="assignment closed")
        if self.due_at is not None and now > self.due_at:
            raise SurveyAssignmentSubmissionNotAllowedError(reason="assignment due date passed")


class SurveySubmission(Entity[SurveySubmissionId]):
    def __init__(
        self,
        *,
        id_: SurveySubmissionId,
        assignment_id: SurveyAssignmentId,
        assignee_user_id: UserId,
        answers: dict[str, Any],
        submitted_at: datetime,
    ) -> None:
        super().__init__(id_=id_)
        self.assignment_id = assignment_id
        self.assignee_user_id = assignee_user_id
        self.answers = answers
        self.submitted_at = submitted_at

    def overwrite(self, *, answers: dict[str, Any], submitted_at: datetime) -> None:
        self.answers = answers
        self.submitted_at = submitted_at


class SurveyResultAccessAudit(Entity[SurveyResultAccessAuditId]):
    def __init__(
        self,
        *,
        id_: SurveyResultAccessAuditId,
        actor_user_id: UserId,
        assignment_id: SurveyAssignmentId,
        action: str,
        occurred_at: datetime,
    ) -> None:
        super().__init__(id_=id_)
        self.actor_user_id = actor_user_id
        self.assignment_id = assignment_id
        self.action = action
        self.occurred_at = occurred_at
