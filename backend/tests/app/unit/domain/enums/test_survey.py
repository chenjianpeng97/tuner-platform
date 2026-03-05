from app.domain.enums.survey import (
    QuestionType,
    SurveyAssignmentStatus,
)


def test_question_type_values_are_stable() -> None:
    assert QuestionType.SINGLE_CHOICE.value == "single_choice"
    assert QuestionType.MULTI_CHOICE.value == "multi_choice"
    assert QuestionType.TEXT.value == "text"


def test_assignment_status_values_are_stable() -> None:
    assert SurveyAssignmentStatus.IN_PROGRESS.value == "in_progress"
    assert SurveyAssignmentStatus.COMPLETED.value == "completed"
