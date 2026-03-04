from app.application.common.ports.survey_audit_command_gateway import (
    SurveyAuditCommandGateway,
)
from app.application.common.ports.survey_audit_query_gateway import (
    SurveyAuditLogQM,
    SurveyAuditQueryGateway,
)
from app.application.common.ports.survey_assignment_command_gateway import (
    SurveyAssignmentCommandGateway,
)
from app.application.common.ports.survey_query_gateway import (
    AssignmentProgressQM,
    SurveyAssignmentDetailQM,
    SurveyAssignmentListItemQM,
    SurveyAssignmentSummaryQM,
    SurveyQueryGateway,
    SurveySubmissionDetailQM,
)
from app.application.common.ports.survey_template_command_gateway import (
    SurveyTemplateCommandGateway,
)


def test_survey_template_command_gateway_defines_core_methods() -> None:
    assert hasattr(SurveyTemplateCommandGateway, "add")
    assert hasattr(SurveyTemplateCommandGateway, "read_by_id")
    assert hasattr(SurveyTemplateCommandGateway, "read_version_by_id")
    assert hasattr(SurveyTemplateCommandGateway, "save_version")


def test_survey_assignment_command_gateway_defines_core_methods() -> None:
    assert hasattr(SurveyAssignmentCommandGateway, "add")
    assert hasattr(SurveyAssignmentCommandGateway, "read_by_id")
    assert hasattr(SurveyAssignmentCommandGateway, "update")
    assert hasattr(SurveyAssignmentCommandGateway, "read_submission")
    assert hasattr(SurveyAssignmentCommandGateway, "save_submission")


def test_survey_audit_gateways_define_core_methods() -> None:
    assert set(SurveyAuditLogQM.__annotations__) == {
        "id_",
        "actor_user_id",
        "assignment_id",
        "action",
        "occurred_at",
    }
    assert hasattr(SurveyAuditCommandGateway, "add")
    assert hasattr(SurveyAuditQueryGateway, "read_logs")


def test_survey_query_gateway_query_models_have_required_fields() -> None:
    assert set(AssignmentProgressQM.__annotations__) == {
        "assignment_id",
        "assignee_count",
        "submitted_count",
        "ratio",
        "status",
    }
    assert set(SurveySubmissionDetailQM.__annotations__) == {
        "assignment_id",
        "assignee_user_id",
        "answers",
        "submitted_at",
    }
    assert set(SurveyAssignmentListItemQM.__annotations__) == {
        "id_",
        "template_version_id",
        "status",
        "due_at",
        "assignee_count",
        "submitted_count",
        "ratio",
    }
    assert set(SurveyAssignmentDetailQM.__annotations__) == {
        "id_",
        "template_version_id",
        "status",
        "due_at",
        "assignee_user_ids",
        "assignee_count",
        "submitted_count",
        "ratio",
    }
    assert set(SurveyAssignmentSummaryQM.__annotations__) == {
        "assignment_id",
        "choice_counts",
        "text_answers",
    }
    assert hasattr(SurveyQueryGateway, "read_assignments")
    assert hasattr(SurveyQueryGateway, "read_assignment_by_id")
    assert hasattr(SurveyQueryGateway, "read_assignment_progress")
    assert hasattr(SurveyQueryGateway, "read_assignment_submissions")
    assert hasattr(SurveyQueryGateway, "read_assignment_summary")
