from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4
from unittest.mock import AsyncMock

import pytest

from app.application.commands.create_survey_template import (
    CreateSurveyTemplateInteractor,
    CreateSurveyTemplateRequest,
)
from app.application.commands.publish_survey_template import (
    PublishSurveyTemplateInteractor,
    PublishSurveyTemplateRequest,
)
from app.application.commands.update_survey_template import (
    UpdateSurveyTemplateInteractor,
    UpdateSurveyTemplateRequest,
)
from app.application.queries.get_survey_template import (
    GetSurveyTemplateQuery,
    GetSurveyTemplateQueryService,
)
from app.application.queries.list_survey_templates import (
    ListSurveyTemplatesQueryService,
)
from app.domain.entities.survey import SurveyQuestion, SurveyTemplate
from app.domain.enums.survey import QuestionType
from app.domain.exceptions.survey import SurveyTemplateNotFoundError
from app.domain.value_objects.survey import SurveyTemplateId


class _TemplateGatewayStub:
    def __init__(self) -> None:
        self.added_template: SurveyTemplate | None = None
        self.saved_version: Any = None
        self.template: SurveyTemplate | None = None
        self.next_version_no = 1

    def add(self, template: SurveyTemplate) -> None:
        self.added_template = template

    async def read_by_id(self, template_id: SurveyTemplateId, for_update: bool = False) -> SurveyTemplate | None:
        return self.template

    async def update(self, template: SurveyTemplate) -> None:
        self.template = template

    async def read_version_by_id(self, version_id: Any, for_update: bool = False) -> Any:
        return None

    def save_version(self, template_version: Any) -> None:
        self.saved_version = template_version

    async def next_published_version_number(self, template_id: SurveyTemplateId) -> int:
        return self.next_version_no


class _QueryGatewayStub:
    def __init__(self) -> None:
        self.templates: list[dict[str, Any]] = []
        self.template_detail: dict[str, Any] | None = None

    async def read_templates(self) -> list[dict[str, Any]]:
        return self.templates

    async def read_template_by_id(self, template_id: UUID) -> dict[str, Any] | None:
        return self.template_detail

    async def read_assignment_progress(self, assignment_id: UUID) -> Any:
        raise NotImplementedError

    async def read_assignment_submissions(self, assignment_id: UUID) -> Any:
        raise NotImplementedError

    async def read_assignment_summary(self, assignment_id: UUID) -> Any:
        raise NotImplementedError


def _sample_question() -> SurveyQuestion:
    return SurveyQuestion(
        key="q1",
        title="Your role",
        question_type=QuestionType.SINGLE_CHOICE,
        required=True,
        options=("dev", "pm"),
    )


@pytest.mark.asyncio
async def test_create_template_interactor_creates_template_and_commits() -> None:
    gateway = _TemplateGatewayStub()
    flusher = AsyncMock()
    tx_manager = AsyncMock()

    interactor = CreateSurveyTemplateInteractor(
        survey_template_command_gateway=gateway,
        flusher=flusher,
        transaction_manager=tx_manager,
    )

    response = await interactor.execute(
        CreateSurveyTemplateRequest(name="Template A", questions=[_sample_question()])
    )

    assert isinstance(response["id"], UUID)
    assert gateway.added_template is not None
    assert gateway.added_template.name == "Template A"
    flusher.flush.assert_awaited_once()
    tx_manager.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_template_interactor_raises_not_found_when_template_missing() -> None:
    gateway = _TemplateGatewayStub()
    flusher = AsyncMock()
    tx_manager = AsyncMock()
    template_id = uuid4()

    interactor = UpdateSurveyTemplateInteractor(
        survey_template_command_gateway=gateway,
        flusher=flusher,
        transaction_manager=tx_manager,
    )

    with pytest.raises(SurveyTemplateNotFoundError):
        await interactor.execute(
            UpdateSurveyTemplateRequest(
                template_id=template_id,
                name="Updated",
                questions=[_sample_question()],
            )
        )


@pytest.mark.asyncio
async def test_publish_template_interactor_publishes_new_version_and_commits() -> None:
    gateway = _TemplateGatewayStub()
    template_id = SurveyTemplateId(uuid4())
    gateway.template = SurveyTemplate(
        id_=template_id,
        name="Template A",
        questions=[_sample_question()],
    )
    gateway.next_version_no = 2
    flusher = AsyncMock()
    tx_manager = AsyncMock()

    interactor = PublishSurveyTemplateInteractor(
        survey_template_command_gateway=gateway,
        flusher=flusher,
        transaction_manager=tx_manager,
    )

    response = await interactor.execute(
        PublishSurveyTemplateRequest(template_id=template_id.value)
    )

    assert isinstance(response["version_id"], UUID)
    assert gateway.saved_version is not None
    assert gateway.saved_version.version == 2
    assert gateway.saved_version.template_id == template_id
    flusher.flush.assert_awaited_once()
    tx_manager.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_templates_query_service_returns_gateway_result() -> None:
    gateway = _QueryGatewayStub()
    gateway.templates = [{"id_": uuid4(), "name": "n1", "latest_published_version_id": None}]

    query_service = ListSurveyTemplatesQueryService(survey_query_gateway=gateway)

    result = await query_service.execute()

    assert result == gateway.templates


@pytest.mark.asyncio
async def test_get_template_query_service_raises_not_found_when_missing() -> None:
    gateway = _QueryGatewayStub()
    query_service = GetSurveyTemplateQueryService(survey_query_gateway=gateway)

    with pytest.raises(SurveyTemplateNotFoundError):
        await query_service.execute(GetSurveyTemplateQuery(template_id=uuid4()))
