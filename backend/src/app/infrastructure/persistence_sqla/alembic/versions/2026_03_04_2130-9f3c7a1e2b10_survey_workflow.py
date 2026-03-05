"""survey workflow normalized tables

Revision ID: 9f3c7a1e2b10
Revises: e325187c1eeb
Create Date: 2026-03-04 21:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "9f3c7a1e2b10"
down_revision: Union[str, None] = "e325187c1eeb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    sa.Enum(
        "SINGLE_CHOICE",
        "MULTI_CHOICE",
        "TEXT",
        name="questiontype",
    ).create(op.get_bind())
    sa.Enum(
        "IN_PROGRESS",
        "COMPLETED",
        name="surveyassignmentstatus",
    ).create(op.get_bind())

    op.create_table(
        "survey_templates",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_survey_templates")),
    )

    op.create_table(
        "survey_template_versions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("template_id", sa.UUID(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("is_published", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["template_id"],
            ["survey_templates.id"],
            name=op.f("fk_survey_template_versions_template_id_survey_templates"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_survey_template_versions")),
        sa.UniqueConstraint(
            "template_id",
            "version",
            name="uq_survey_template_versions_template_id_version",
        ),
    )
    op.create_index(
        "ix_survey_template_versions_template_id",
        "survey_template_versions",
        ["template_id"],
    )
    op.create_index(
        "ix_survey_template_versions_template_id_is_published",
        "survey_template_versions",
        ["template_id", "is_published"],
    )

    op.create_table(
        "survey_template_questions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("template_version_id", sa.UUID(), nullable=False),
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column(
            "question_type",
            postgresql.ENUM(
                "SINGLE_CHOICE",
                "MULTI_CHOICE",
                "TEXT",
                name="questiontype",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("required", sa.Boolean(), nullable=False),
        sa.Column("order_no", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["template_version_id"],
            ["survey_template_versions.id"],
            name=op.f(
                "fk_survey_template_questions_template_version_id_survey_template_versions"
            ),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_survey_template_questions")),
        sa.UniqueConstraint(
            "template_version_id",
            "key",
            name="uq_survey_template_questions_template_version_id_key",
        ),
    )
    op.create_index(
        "ix_survey_template_questions_template_version_order_no",
        "survey_template_questions",
        ["template_version_id", "order_no"],
    )

    op.create_table(
        "survey_template_question_options",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("question_id", sa.UUID(), nullable=False),
        sa.Column("value", sa.String(length=255), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("order_no", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["survey_template_questions.id"],
            name=op.f(
                "fk_survey_template_question_options_question_id_survey_template_questions"
            ),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_survey_template_question_options"),
        ),
    )
    op.create_index(
        "ix_survey_template_question_options_question_id_order_no",
        "survey_template_question_options",
        ["question_id", "order_no"],
    )

    op.create_table(
        "survey_assignments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("template_version_id", sa.UUID(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "IN_PROGRESS",
                "COMPLETED",
                name="surveyassignmentstatus",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["template_version_id"],
            ["survey_template_versions.id"],
            name=op.f("fk_survey_assignments_template_version_id_survey_template_versions"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_survey_assignments")),
    )
    op.create_index(
        "ix_survey_assignments_template_version_id",
        "survey_assignments",
        ["template_version_id"],
    )
    op.create_index("ix_survey_assignments_status", "survey_assignments", ["status"])
    op.create_index("ix_survey_assignments_due_at", "survey_assignments", ["due_at"])

    op.create_table(
        "survey_assignment_assignees",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("assignment_id", sa.UUID(), nullable=False),
        sa.Column("assignee_user_id", sa.UUID(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["assignment_id"],
            ["survey_assignments.id"],
            name=op.f("fk_survey_assignment_assignees_assignment_id_survey_assignments"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_survey_assignment_assignees")),
        sa.UniqueConstraint(
            "assignment_id",
            "assignee_user_id",
            name="uq_survey_assignment_assignees_assignment_id_assignee_user_id",
        ),
    )
    op.create_index(
        "ix_survey_assignment_assignees_assignee_user_id",
        "survey_assignment_assignees",
        ["assignee_user_id"],
    )
    op.create_index(
        "ix_survey_assignment_assignees_assignment_id_submitted_at",
        "survey_assignment_assignees",
        ["assignment_id", "submitted_at"],
    )

    op.create_table(
        "survey_submissions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("assignment_id", sa.UUID(), nullable=False),
        sa.Column("assignee_user_id", sa.UUID(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["assignment_id"],
            ["survey_assignments.id"],
            name=op.f("fk_survey_submissions_assignment_id_survey_assignments"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_survey_submissions")),
        sa.UniqueConstraint(
            "assignment_id",
            "assignee_user_id",
            name="uq_survey_submissions_assignment_id_assignee_user_id",
        ),
    )
    op.create_index(
        "ix_survey_submissions_assignment_id",
        "survey_submissions",
        ["assignment_id"],
    )
    op.create_index(
        "ix_survey_submissions_assignee_user_id",
        "survey_submissions",
        ["assignee_user_id"],
    )

    op.create_table(
        "survey_submission_answers",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submission_id", sa.UUID(), nullable=False),
        sa.Column("question_key", sa.String(length=64), nullable=False),
        sa.Column("answer_value", sa.String(length=2048), nullable=False),
        sa.Column("order_no", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["submission_id"],
            ["survey_submissions.id"],
            name=op.f("fk_survey_submission_answers_submission_id_survey_submissions"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_survey_submission_answers")),
    )
    op.create_index(
        "ix_survey_submission_answers_submission_id_order_no",
        "survey_submission_answers",
        ["submission_id", "order_no"],
    )

    op.create_table(
        "survey_result_access_audits",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("actor_user_id", sa.UUID(), nullable=False),
        sa.Column("assignment_id", sa.UUID(), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["assignment_id"],
            ["survey_assignments.id"],
            name=op.f("fk_survey_result_access_audits_assignment_id_survey_assignments"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_survey_result_access_audits")),
    )
    op.create_index(
        "ix_survey_result_access_audits_assignment_id_occurred_at",
        "survey_result_access_audits",
        ["assignment_id", "occurred_at"],
    )
    op.create_index(
        "ix_survey_result_access_audits_occurred_at",
        "survey_result_access_audits",
        ["occurred_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_survey_result_access_audits_occurred_at",
        table_name="survey_result_access_audits",
    )
    op.drop_index(
        "ix_survey_result_access_audits_assignment_id_occurred_at",
        table_name="survey_result_access_audits",
    )
    op.drop_table("survey_result_access_audits")

    op.drop_index(
        "ix_survey_submission_answers_submission_id_order_no",
        table_name="survey_submission_answers",
    )
    op.drop_table("survey_submission_answers")

    op.drop_index(
        "ix_survey_submissions_assignee_user_id",
        table_name="survey_submissions",
    )
    op.drop_index("ix_survey_submissions_assignment_id", table_name="survey_submissions")
    op.drop_table("survey_submissions")

    op.drop_index(
        "ix_survey_assignment_assignees_assignment_id_submitted_at",
        table_name="survey_assignment_assignees",
    )
    op.drop_index(
        "ix_survey_assignment_assignees_assignee_user_id",
        table_name="survey_assignment_assignees",
    )
    op.drop_table("survey_assignment_assignees")

    op.drop_index("ix_survey_assignments_due_at", table_name="survey_assignments")
    op.drop_index("ix_survey_assignments_status", table_name="survey_assignments")
    op.drop_index(
        "ix_survey_assignments_template_version_id",
        table_name="survey_assignments",
    )
    op.drop_table("survey_assignments")

    op.drop_index(
        "ix_survey_template_question_options_question_id_order_no",
        table_name="survey_template_question_options",
    )
    op.drop_table("survey_template_question_options")

    op.drop_index(
        "ix_survey_template_questions_template_version_order_no",
        table_name="survey_template_questions",
    )
    op.drop_table("survey_template_questions")

    op.drop_index(
        "ix_survey_template_versions_template_id_is_published",
        table_name="survey_template_versions",
    )
    op.drop_index(
        "ix_survey_template_versions_template_id",
        table_name="survey_template_versions",
    )
    op.drop_table("survey_template_versions")

    op.drop_table("survey_templates")

    sa.Enum(
        "IN_PROGRESS",
        "COMPLETED",
        name="surveyassignmentstatus",
    ).drop(op.get_bind())
    sa.Enum(
        "SINGLE_CHOICE",
        "MULTI_CHOICE",
        "TEXT",
        name="questiontype",
    ).drop(op.get_bind())
