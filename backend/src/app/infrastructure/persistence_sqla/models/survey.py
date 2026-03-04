from datetime import datetime
from uuid import UUID

from app.domain.enums.survey import QuestionType, SurveyAssignmentStatus


class SurveyTemplateModel:
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime


class SurveyTemplateVersionModel:
    id: UUID
    template_id: UUID
    version: int
    is_published: bool
    created_at: datetime


class SurveyTemplateQuestionModel:
    id: UUID
    template_version_id: UUID
    key: str
    title: str
    question_type: QuestionType
    required: bool
    order_no: int


class SurveyTemplateQuestionOptionModel:
    id: UUID
    question_id: UUID
    value: str
    label: str
    order_no: int


class SurveyAssignmentModel:
    id: UUID
    template_version_id: UUID
    status: SurveyAssignmentStatus
    due_at: datetime | None
    created_by: UUID | None
    created_at: datetime
    closed_at: datetime | None


class SurveyAssignmentAssigneeModel:
    id: UUID
    assignment_id: UUID
    assignee_user_id: UUID
    submitted_at: datetime | None


class SurveySubmissionModel:
    id: UUID
    assignment_id: UUID
    assignee_user_id: UUID
    submitted_at: datetime


class SurveySubmissionAnswerModel:
    id: UUID
    submission_id: UUID
    question_key: str
    answer_value: str
    order_no: int


class SurveyResultAccessAuditModel:
    id: UUID
    actor_user_id: UUID
    assignment_id: UUID
    action: str
    occurred_at: datetime
