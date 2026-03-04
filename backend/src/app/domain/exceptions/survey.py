from app.domain.exceptions.base import DomainError


class SurveyAssignmentSubmissionNotAllowedError(DomainError):
    def __init__(self, *, reason: str) -> None:
        super().__init__(f"Survey assignment submission is not allowed: {reason}.")


class SurveyTemplateNotFoundError(DomainError):
    def __init__(self) -> None:
        super().__init__("Survey template is not found.")


class SurveyTemplateVersionNotFoundError(DomainError):
    def __init__(self) -> None:
        super().__init__("Survey template version is not found.")


class SurveyAssignmentNotFoundError(DomainError):
    def __init__(self) -> None:
        super().__init__("Survey assignment is not found.")


class SurveyAssignmentAssigneePermissionError(DomainError):
    def __init__(self) -> None:
        super().__init__("Only assignment assignee can access my submission.")
