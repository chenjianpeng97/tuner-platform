from dataclasses import dataclass
from uuid import UUID

from app.domain.value_objects.base import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class SurveyTemplateId(ValueObject):
    value: UUID


@dataclass(frozen=True, slots=True, repr=False)
class SurveyTemplateVersionId(ValueObject):
    value: UUID


@dataclass(frozen=True, slots=True, repr=False)
class SurveyAssignmentId(ValueObject):
    value: UUID


@dataclass(frozen=True, slots=True, repr=False)
class SurveySubmissionId(ValueObject):
    value: UUID


@dataclass(frozen=True, slots=True, repr=False)
class SurveyResultAccessAuditId(ValueObject):
    value: UUID
