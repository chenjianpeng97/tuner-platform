from abc import abstractmethod
from typing import Protocol

from app.domain.entities.survey import SurveyTemplate, SurveyTemplateVersion
from app.domain.value_objects.survey import SurveyTemplateId, SurveyTemplateVersionId


class SurveyTemplateCommandGateway(Protocol):
    @abstractmethod
    def add(self, template: SurveyTemplate) -> None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def read_by_id(
        self,
        template_id: SurveyTemplateId,
        for_update: bool = False,
    ) -> SurveyTemplate | None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def update(self, template: SurveyTemplate) -> None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def read_version_by_id(
        self,
        version_id: SurveyTemplateVersionId,
        for_update: bool = False,
    ) -> SurveyTemplateVersion | None:
        """:raises DataMapperError:"""

    @abstractmethod
    def save_version(self, template_version: SurveyTemplateVersion) -> None:
        """:raises DataMapperError:"""

    @abstractmethod
    async def next_published_version_number(
        self,
        template_id: SurveyTemplateId,
    ) -> int:
        """:raises DataMapperError:"""
