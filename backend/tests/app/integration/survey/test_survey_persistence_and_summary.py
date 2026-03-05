from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.domain.entities.survey import (
    SurveyAssignment,
    SurveyQuestion,
    SurveySubmission,
    SurveyTemplate,
    SurveyTemplateVersion,
)
from app.domain.enums.survey import QuestionType
from app.domain.value_objects.survey import (
    SurveyAssignmentId,
    SurveySubmissionId,
    SurveyTemplateId,
    SurveyTemplateVersionId,
)
from app.domain.value_objects.user_id import UserId
from app.infrastructure.adapters.survey_assignment_data_mapper_sqla import (
    SqlaSurveyAssignmentDataMapper,
)
from app.infrastructure.adapters.survey_reader_sqla import SqlaSurveyReader
from app.infrastructure.adapters.survey_template_data_mapper_sqla import (
    SqlaSurveyTemplateDataMapper,
)
from app.infrastructure.persistence_sqla.mappings.all import map_tables
from app.infrastructure.persistence_sqla.registry import mapper_registry


class SyncBackedAsyncSession:
    def __init__(self, sync_session: Session) -> None:
        self._sync_session = sync_session

    def add(self, instance: object) -> None:
        self._sync_session.add(instance)

    async def execute(self, stmt):
        return self._sync_session.execute(stmt)


def _ensure_mapped() -> None:
    try:
        map_tables()
    except Exception as err:  # pragma: no cover - idempotent guard for repeated test runs
        if "already has a primary mapper" not in str(err):
            raise


def _make_sync_session() -> Session:
    _ensure_mapped()
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    mapper_registry.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    return factory()


def _build_questions() -> tuple[SurveyQuestion, ...]:
    return (
        SurveyQuestion(
            key="role",
            title="Role",
            question_type=QuestionType.SINGLE_CHOICE,
            required=True,
            options=("dev", "qa"),
        ),
        SurveyQuestion(
            key="tools",
            title="Tools",
            question_type=QuestionType.MULTI_CHOICE,
            required=False,
            options=("dashboard", "api", "cli"),
        ),
        SurveyQuestion(
            key="feedback",
            title="Feedback",
            question_type=QuestionType.TEXT,
            required=False,
            options=(),
        ),
    )


@pytest.mark.asyncio
async def test_submission_overwrite_keeps_single_progress_increment() -> None:
    sync_session = _make_sync_session()
    session = SyncBackedAsyncSession(sync_session)
    template_mapper = SqlaSurveyTemplateDataMapper(session)  # type: ignore[arg-type]
    assignment_mapper = SqlaSurveyAssignmentDataMapper(session)  # type: ignore[arg-type]
    reader = SqlaSurveyReader(session)  # type: ignore[arg-type]

    template_id = SurveyTemplateId(uuid4())
    version_id = SurveyTemplateVersionId(uuid4())
    assignment_id = SurveyAssignmentId(uuid4())
    user_1 = UserId(uuid4())
    user_2 = UserId(uuid4())

    template_mapper.add(
        SurveyTemplate(id_=template_id, name="Platform Feedback", questions=_build_questions())
    )
    template_mapper.save_version(
        SurveyTemplateVersion(
            id_=version_id,
            template_id=template_id,
            version=1,
            questions=_build_questions(),
        )
    )
    assignment_mapper.add(
        SurveyAssignment(
            id_=assignment_id,
            template_version_id=version_id,
            assignee_user_ids=(user_1, user_2),
            due_at=None,
        )
    )
    sync_session.commit()

    submission_id = SurveySubmissionId(uuid4())
    first_submit = datetime.now(UTC)
    await assignment_mapper.save_submission(
        SurveySubmission(
            id_=submission_id,
            assignment_id=assignment_id,
            assignee_user_id=user_1,
            answers={"role": "dev", "tools": ["dashboard"], "feedback": "v1"},
            submitted_at=first_submit,
        )
    )
    sync_session.commit()

    overwritten_submit = datetime.now(UTC)
    await assignment_mapper.save_submission(
        SurveySubmission(
            id_=submission_id,
            assignment_id=assignment_id,
            assignee_user_id=user_1,
            answers={"role": "qa", "tools": ["api"], "feedback": "v2"},
            submitted_at=overwritten_submit,
        )
    )
    sync_session.commit()

    detail = await reader.read_assignment_by_id(assignment_id.value)
    assert detail is not None
    assert detail["submitted_count"] == 1
    assert detail["assignee_count"] == 2
    assert detail["ratio"] == 0.5


@pytest.mark.asyncio
async def test_summary_aggregation_reads_latest_persisted_answers() -> None:
    sync_session = _make_sync_session()
    session = SyncBackedAsyncSession(sync_session)
    template_mapper = SqlaSurveyTemplateDataMapper(session)  # type: ignore[arg-type]
    assignment_mapper = SqlaSurveyAssignmentDataMapper(session)  # type: ignore[arg-type]
    reader = SqlaSurveyReader(session)  # type: ignore[arg-type]

    template_id = SurveyTemplateId(uuid4())
    version_id = SurveyTemplateVersionId(uuid4())
    assignment_id = SurveyAssignmentId(uuid4())
    user_1 = UserId(uuid4())
    user_2 = UserId(uuid4())

    questions = _build_questions()
    template_mapper.add(SurveyTemplate(id_=template_id, name="Platform Feedback", questions=questions))
    template_mapper.save_version(
        SurveyTemplateVersion(
            id_=version_id,
            template_id=template_id,
            version=1,
            questions=questions,
        )
    )
    assignment_mapper.add(
        SurveyAssignment(
            id_=assignment_id,
            template_version_id=version_id,
            assignee_user_ids=(user_1, user_2),
            due_at=None,
        )
    )
    sync_session.commit()

    await assignment_mapper.save_submission(
        SurveySubmission(
            id_=SurveySubmissionId(uuid4()),
            assignment_id=assignment_id,
            assignee_user_id=user_1,
            answers={
                "role": "dev",
                "tools": ["dashboard", "api"],
                "feedback": "need better filters",
            },
            submitted_at=datetime.now(UTC),
        )
    )
    await assignment_mapper.save_submission(
        SurveySubmission(
            id_=SurveySubmissionId(uuid4()),
            assignment_id=assignment_id,
            assignee_user_id=user_2,
            answers={"role": "qa", "tools": ["api"], "feedback": "looks good"},
            submitted_at=datetime.now(UTC),
        )
    )
    sync_session.commit()

    submissions = await reader.read_assignment_submissions(assignment_id.value)
    assert len(submissions) == 2
    answers_by_user = {row["assignee_user_id"]: row["answers"] for row in submissions}
    assert answers_by_user[user_1.value]["role"] == "dev"
    assert answers_by_user[user_2.value]["role"] == "qa"

    summary = await reader.read_assignment_summary(assignment_id.value)
    assert summary["choice_counts"]["role"] == {"dev": 1, "qa": 1}
    assert summary["choice_counts"]["tools"] == {"dashboard": 1, "api": 2}
    assert sorted(summary["text_answers"]["feedback"]) == [
        "looks good",
        "need better filters",
    ]
