from enum import StrEnum


class QuestionType(StrEnum):
    SINGLE_CHOICE = "single_choice"
    MULTI_CHOICE = "multi_choice"
    TEXT = "text"


class SurveyAssignmentStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
