from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    UniqueConstraint,
)

from app.domain.enums.survey import QuestionType, SurveyAssignmentStatus
from app.infrastructure.persistence_sqla.models.survey import (
    SurveyAssignmentAssigneeModel,
    SurveyAssignmentModel,
    SurveyResultAccessAuditModel,
    SurveySubmissionAnswerModel,
    SurveySubmissionModel,
    SurveyTemplateModel,
    SurveyTemplateQuestionModel,
    SurveyTemplateQuestionOptionModel,
    SurveyTemplateVersionModel,
)
from app.infrastructure.persistence_sqla.registry import mapper_registry

survey_templates_table = Table(
    "survey_templates",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("name", String(255), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

survey_template_versions_table = Table(
    "survey_template_versions",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column(
        "template_id",
        UUID(as_uuid=True),
        ForeignKey("survey_templates.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    Column("version", Integer, nullable=False),
    Column("is_published", Boolean, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    UniqueConstraint(
        "template_id",
        "version",
        name="uq_survey_template_versions_template_id_version",
    ),
)

survey_template_questions_table = Table(
    "survey_template_questions",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column(
        "template_version_id",
        UUID(as_uuid=True),
        ForeignKey("survey_template_versions.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("key", String(64), nullable=False),
    Column("title", String(512), nullable=False),
    Column("question_type", Enum(QuestionType, name="questiontype"), nullable=False),
    Column("required", Boolean, nullable=False),
    Column("order_no", Integer, nullable=False),
    UniqueConstraint(
        "template_version_id",
        "key",
        name="uq_survey_template_questions_template_version_id_key",
    ),
)

survey_template_question_options_table = Table(
    "survey_template_question_options",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column(
        "question_id",
        UUID(as_uuid=True),
        ForeignKey("survey_template_questions.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("value", String(255), nullable=False),
    Column("label", String(255), nullable=False),
    Column("order_no", Integer, nullable=False),
)

survey_assignments_table = Table(
    "survey_assignments",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column(
        "template_version_id",
        UUID(as_uuid=True),
        ForeignKey("survey_template_versions.id", ondelete="RESTRICT"),
        nullable=False,
    ),
    Column(
        "status",
        Enum(SurveyAssignmentStatus, name="surveyassignmentstatus"),
        nullable=False,
    ),
    Column("due_at", DateTime(timezone=True), nullable=True),
    Column("created_by", UUID(as_uuid=True), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("closed_at", DateTime(timezone=True), nullable=True),
)

survey_assignment_assignees_table = Table(
    "survey_assignment_assignees",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column(
        "assignment_id",
        UUID(as_uuid=True),
        ForeignKey("survey_assignments.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("assignee_user_id", UUID(as_uuid=True), nullable=False),
    Column("submitted_at", DateTime(timezone=True), nullable=True),
    UniqueConstraint(
        "assignment_id",
        "assignee_user_id",
        name="uq_survey_assignment_assignees_assignment_id_assignee_user_id",
    ),
)

survey_submissions_table = Table(
    "survey_submissions",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column(
        "assignment_id",
        UUID(as_uuid=True),
        ForeignKey("survey_assignments.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("assignee_user_id", UUID(as_uuid=True), nullable=False),
    Column("submitted_at", DateTime(timezone=True), nullable=False),
    UniqueConstraint(
        "assignment_id",
        "assignee_user_id",
        name="uq_survey_submissions_assignment_id_assignee_user_id",
    ),
)

survey_submission_answers_table = Table(
    "survey_submission_answers",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column(
        "submission_id",
        UUID(as_uuid=True),
        ForeignKey("survey_submissions.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("question_key", String(64), nullable=False),
    Column("answer_value", String(2048), nullable=False),
    Column("order_no", Integer, nullable=False),
)

survey_result_access_audits_table = Table(
    "survey_result_access_audits",
    mapper_registry.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("actor_user_id", UUID(as_uuid=True), nullable=False),
    Column(
        "assignment_id",
        UUID(as_uuid=True),
        ForeignKey("survey_assignments.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("action", String(64), nullable=False),
    Column("occurred_at", DateTime(timezone=True), nullable=False),
)


def map_survey_tables() -> None:
    mapper_registry.map_imperatively(SurveyTemplateModel, survey_templates_table)
    mapper_registry.map_imperatively(
        SurveyTemplateVersionModel,
        survey_template_versions_table,
    )
    mapper_registry.map_imperatively(
        SurveyTemplateQuestionModel,
        survey_template_questions_table,
    )
    mapper_registry.map_imperatively(
        SurveyTemplateQuestionOptionModel,
        survey_template_question_options_table,
    )
    mapper_registry.map_imperatively(SurveyAssignmentModel, survey_assignments_table)
    mapper_registry.map_imperatively(
        SurveyAssignmentAssigneeModel,
        survey_assignment_assignees_table,
    )
    mapper_registry.map_imperatively(SurveySubmissionModel, survey_submissions_table)
    mapper_registry.map_imperatively(
        SurveySubmissionAnswerModel,
        survey_submission_answers_table,
    )
    mapper_registry.map_imperatively(
        SurveyResultAccessAuditModel,
        survey_result_access_audits_table,
    )
