from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import delete, select, update
from sqlalchemy.exc import SQLAlchemyError

from app.application.common.ports.survey_template_command_gateway import (
    SurveyTemplateCommandGateway,
)
from app.domain.entities.survey import (
    SurveyQuestion,
    SurveyTemplate,
    SurveyTemplateVersion,
)
from app.domain.value_objects.survey import (
    SurveyTemplateId,
    SurveyTemplateVersionId,
)
from app.infrastructure.adapters.constants import DB_QUERY_FAILED
from app.infrastructure.adapters.types import MainAsyncSession
from app.infrastructure.exceptions.gateway import DataMapperError
from app.infrastructure.persistence_sqla.mappings.survey import (
    survey_template_question_options_table,
    survey_template_questions_table,
    survey_template_versions_table,
    survey_templates_table,
)
from app.infrastructure.persistence_sqla.models.survey import (
    SurveyTemplateModel,
    SurveyTemplateQuestionModel,
    SurveyTemplateQuestionOptionModel,
    SurveyTemplateVersionModel,
)


class SqlaSurveyTemplateDataMapper(SurveyTemplateCommandGateway):
    def __init__(self, session: MainAsyncSession) -> None:
        self._session = session

    def add(self, template: SurveyTemplate) -> None:
        """:raises DataMapperError:"""
        created_at = datetime.now(UTC)
        template_model = SurveyTemplateModel()
        template_model.id = template.id_.value
        template_model.name = template.name
        template_model.created_at = created_at
        template_model.updated_at = created_at
        self._session.add(template_model)

        draft_version_model = SurveyTemplateVersionModel()
        draft_version_model.id = uuid4()
        draft_version_model.template_id = template.id_.value
        draft_version_model.version = 0
        draft_version_model.is_published = False
        draft_version_model.created_at = created_at
        self._session.add(draft_version_model)

        for order_no, question in enumerate(template.questions):
            question_model = SurveyTemplateQuestionModel()
            question_model.id = uuid4()
            question_model.template_version_id = draft_version_model.id
            question_model.key = question.key
            question_model.title = question.title
            question_model.question_type = question.question_type
            question_model.required = question.required
            question_model.order_no = order_no
            self._session.add(question_model)

            for option_order, option in enumerate(question.options):
                option_model = SurveyTemplateQuestionOptionModel()
                option_model.id = uuid4()
                option_model.question_id = question_model.id
                option_model.value = option
                option_model.label = option
                option_model.order_no = option_order
                self._session.add(option_model)

    async def read_by_id(
        self,
        template_id: SurveyTemplateId,
        for_update: bool = False,
    ) -> SurveyTemplate | None:
        """:raises DataMapperError:"""
        template_stmt = select(
            survey_templates_table.c.id,
            survey_templates_table.c.name,
        ).where(survey_templates_table.c.id == template_id.value)

        draft_stmt = (
            select(
                survey_template_versions_table.c.id,
            )
            .where(
                survey_template_versions_table.c.template_id == template_id.value,
                survey_template_versions_table.c.is_published.is_(False),
            )
            .order_by(survey_template_versions_table.c.created_at.desc())
            .limit(1)
        )
        if for_update:
            template_stmt = template_stmt.with_for_update()
            draft_stmt = draft_stmt.with_for_update()

        try:
            template_row = (await self._session.execute(template_stmt)).one_or_none()
            if template_row is None:
                return None
            draft_row = (await self._session.execute(draft_stmt)).one_or_none()
            draft_version_id: UUID | None = draft_row.id if draft_row is not None else None
            questions = await self._read_questions_for_version(draft_version_id)
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err

        return SurveyTemplate(
            id_=SurveyTemplateId(template_row.id),
            name=template_row.name,
            questions=questions,
        )

    async def update(self, template: SurveyTemplate) -> None:
        """:raises DataMapperError:"""
        draft_stmt = (
            select(survey_template_versions_table.c.id)
            .where(
                survey_template_versions_table.c.template_id == template.id_.value,
                survey_template_versions_table.c.is_published.is_(False),
            )
            .order_by(survey_template_versions_table.c.created_at.desc())
            .limit(1)
            .with_for_update()
        )
        try:
            await self._session.execute(
                update(survey_templates_table)
                .where(survey_templates_table.c.id == template.id_.value)
                .values(name=template.name, updated_at=datetime.now(UTC))
            )
            draft_row = (await self._session.execute(draft_stmt)).one_or_none()
            if draft_row is None:
                draft_model = SurveyTemplateVersionModel()
                draft_model.id = uuid4()
                draft_model.template_id = template.id_.value
                draft_model.version = 0
                draft_model.is_published = False
                draft_model.created_at = datetime.now(UTC)
                self._session.add(draft_model)
                draft_version_id = draft_model.id
            else:
                draft_version_id = draft_row.id

            question_ids_stmt = select(survey_template_questions_table.c.id).where(
                survey_template_questions_table.c.template_version_id == draft_version_id,
            )
            question_ids = [
                row.id for row in (await self._session.execute(question_ids_stmt)).all()
            ]
            if question_ids:
                await self._session.execute(
                    delete(survey_template_question_options_table).where(
                        survey_template_question_options_table.c.question_id.in_(question_ids),
                    )
                )
            await self._session.execute(
                delete(survey_template_questions_table).where(
                    survey_template_questions_table.c.template_version_id == draft_version_id,
                )
            )

            for order_no, question in enumerate(template.questions):
                question_model = SurveyTemplateQuestionModel()
                question_model.id = uuid4()
                question_model.template_version_id = draft_version_id
                question_model.key = question.key
                question_model.title = question.title
                question_model.question_type = question.question_type
                question_model.required = question.required
                question_model.order_no = order_no
                self._session.add(question_model)

                for option_order, option in enumerate(question.options):
                    option_model = SurveyTemplateQuestionOptionModel()
                    option_model.id = uuid4()
                    option_model.question_id = question_model.id
                    option_model.value = option
                    option_model.label = option
                    option_model.order_no = option_order
                    self._session.add(option_model)
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err

    async def read_version_by_id(
        self,
        version_id: SurveyTemplateVersionId,
        for_update: bool = False,
    ) -> SurveyTemplateVersion | None:
        """:raises DataMapperError:"""
        stmt = select(
            survey_template_versions_table.c.id,
            survey_template_versions_table.c.template_id,
            survey_template_versions_table.c.version,
            survey_template_versions_table.c.is_published,
        ).where(survey_template_versions_table.c.id == version_id.value)
        if for_update:
            stmt = stmt.with_for_update()

        try:
            row = (await self._session.execute(stmt)).one_or_none()
            if row is None or not row.is_published:
                return None
            questions = await self._read_questions_for_version(row.id)
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err

        return SurveyTemplateVersion(
            id_=SurveyTemplateVersionId(row.id),
            template_id=SurveyTemplateId(row.template_id),
            version=row.version,
            questions=tuple(questions),
        )

    def save_version(self, template_version: SurveyTemplateVersion) -> None:
        """:raises DataMapperError:"""
        created_at = datetime.now(UTC)
        version_model = SurveyTemplateVersionModel()
        version_model.id = template_version.id_.value
        version_model.template_id = template_version.template_id.value
        version_model.version = template_version.version
        version_model.is_published = True
        version_model.created_at = created_at
        self._session.add(version_model)

        for order_no, question in enumerate(template_version.questions):
            question_model = SurveyTemplateQuestionModel()
            question_model.id = uuid4()
            question_model.template_version_id = template_version.id_.value
            question_model.key = question.key
            question_model.title = question.title
            question_model.question_type = question.question_type
            question_model.required = question.required
            question_model.order_no = order_no
            self._session.add(question_model)

            for option_order, option in enumerate(question.options):
                option_model = SurveyTemplateQuestionOptionModel()
                option_model.id = uuid4()
                option_model.question_id = question_model.id
                option_model.value = option
                option_model.label = option
                option_model.order_no = option_order
                self._session.add(option_model)

    async def next_published_version_number(
        self,
        template_id: SurveyTemplateId,
    ) -> int:
        """:raises DataMapperError:"""
        stmt = (
            select(survey_template_versions_table.c.version)
            .where(
                survey_template_versions_table.c.template_id == template_id.value,
                survey_template_versions_table.c.is_published.is_(True),
            )
            .order_by(survey_template_versions_table.c.version.desc())
            .limit(1)
        )
        try:
            row = (await self._session.execute(stmt)).one_or_none()
        except SQLAlchemyError as err:
            raise DataMapperError(DB_QUERY_FAILED) from err
        if row is None:
            return 1
        return int(row.version) + 1

    async def _read_questions_for_version(
        self,
        template_version_id: UUID | None,
    ) -> list[SurveyQuestion]:
        if template_version_id is None:
            return []
        questions_stmt = (
            select(
                survey_template_questions_table.c.id,
                survey_template_questions_table.c.key,
                survey_template_questions_table.c.title,
                survey_template_questions_table.c.question_type,
                survey_template_questions_table.c.required,
                survey_template_questions_table.c.order_no,
            )
            .where(
                survey_template_questions_table.c.template_version_id
                == template_version_id,
            )
            .order_by(survey_template_questions_table.c.order_no.asc())
        )
        question_rows = (await self._session.execute(questions_stmt)).all()
        if not question_rows:
            return []

        question_ids = [row.id for row in question_rows]
        options_stmt = (
            select(
                survey_template_question_options_table.c.question_id,
                survey_template_question_options_table.c.value,
                survey_template_question_options_table.c.order_no,
            )
            .where(survey_template_question_options_table.c.question_id.in_(question_ids))
            .order_by(survey_template_question_options_table.c.order_no.asc())
        )
        option_rows = (await self._session.execute(options_stmt)).all()
        options_by_question: dict[UUID, list[str]] = {qid: [] for qid in question_ids}
        for option_row in option_rows:
            options_by_question[option_row.question_id].append(option_row.value)

        return [
            SurveyQuestion(
                key=question_row.key,
                title=question_row.title,
                question_type=question_row.question_type,
                required=question_row.required,
                options=tuple(options_by_question[question_row.id]),
            )
            for question_row in question_rows
        ]
