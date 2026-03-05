from __future__ import annotations

import base64
import hashlib
import hmac
from datetime import UTC, datetime
import uuid
from typing import Final

import bcrypt
import jwt
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.setup.config.settings import AppSettings


class RealFixtureRunner:
    ADMIN_USERNAME = "bddadmin"
    ADMIN_PASSWORD = "adminpass1"
    USER_PASSWORD = "testpass1"

    TEMPLATE_ID: Final[uuid.UUID] = uuid.UUID("11111111-1111-1111-1111-111111111111")
    PUBLISHED_TEMPLATE_ID: Final[uuid.UUID] = uuid.UUID(
        "12111111-1111-1111-1111-111111111111",
    )
    TEMPLATE_VERSION_ID: Final[uuid.UUID] = uuid.UUID(
        "21111111-1111-1111-1111-111111111111",
    )
    ASSIGNMENT_ID: Final[uuid.UUID] = uuid.UUID("31111111-1111-1111-1111-111111111111")

    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings
        self._engine: Engine = create_engine(settings.postgres.dsn)

    def prepare_scenario(self) -> dict[str, str]:
        self.ensure_enum_labels_compatibility()
        self.cleanup_database()
        self.seed_baseline_data()
        return self.bootstrap_auth_cookie()

    def ensure_enum_labels_compatibility(self) -> None:
        normalize_sql = text(
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM pg_type t
                    JOIN pg_enum e ON e.enumtypid = t.oid
                    WHERE t.typname = 'questiontype' AND e.enumlabel = 'SINGLE_CHOICE'
                ) THEN
                    ALTER TYPE questiontype RENAME VALUE 'SINGLE_CHOICE' TO 'single_choice';
                END IF;
                IF EXISTS (
                    SELECT 1 FROM pg_type t
                    JOIN pg_enum e ON e.enumtypid = t.oid
                    WHERE t.typname = 'questiontype' AND e.enumlabel = 'MULTI_CHOICE'
                ) THEN
                    ALTER TYPE questiontype RENAME VALUE 'MULTI_CHOICE' TO 'multi_choice';
                END IF;
                IF EXISTS (
                    SELECT 1 FROM pg_type t
                    JOIN pg_enum e ON e.enumtypid = t.oid
                    WHERE t.typname = 'questiontype' AND e.enumlabel = 'TEXT'
                ) THEN
                    ALTER TYPE questiontype RENAME VALUE 'TEXT' TO 'text';
                END IF;
                IF EXISTS (
                    SELECT 1 FROM pg_type t
                    JOIN pg_enum e ON e.enumtypid = t.oid
                    WHERE t.typname = 'surveyassignmentstatus' AND e.enumlabel = 'IN_PROGRESS'
                ) THEN
                    ALTER TYPE surveyassignmentstatus RENAME VALUE 'IN_PROGRESS' TO 'in_progress';
                END IF;
                IF EXISTS (
                    SELECT 1 FROM pg_type t
                    JOIN pg_enum e ON e.enumtypid = t.oid
                    WHERE t.typname = 'surveyassignmentstatus' AND e.enumlabel = 'COMPLETED'
                ) THEN
                    ALTER TYPE surveyassignmentstatus RENAME VALUE 'COMPLETED' TO 'completed';
                END IF;
            END
            $$;
            """
        )
        with self._engine.begin() as connection:
            connection.execute(normalize_sql)

    def cleanup_database(self) -> None:
        cleanup_sql = text(
            """
            DO $$
            DECLARE
                r RECORD;
            BEGIN
                FOR r IN (
                    SELECT tablename
                    FROM pg_tables
                    WHERE schemaname = 'public'
                      AND tablename <> 'alembic_version'
                ) LOOP
                    EXECUTE format(
                        'TRUNCATE TABLE %I.%I RESTART IDENTITY CASCADE',
                        'public',
                        r.tablename
                    );
                END LOOP;
            END
            $$;
            """
        )
        with self._engine.begin() as connection:
            connection.execute(cleanup_sql)

    def seed_baseline_data(self) -> None:
        users = {
            self.ADMIN_USERNAME: {
                "id": uuid.uuid5(uuid.NAMESPACE_DNS, f"bdd-admin:{self.ADMIN_USERNAME}"),
                "role": "SUPER_ADMIN",
                "password": self.ADMIN_PASSWORD,
            },
            "u1": {
                "id": uuid.uuid5(uuid.NAMESPACE_DNS, "bdd-user:u1"),
                "role": "USER",
                "password": self.USER_PASSWORD,
            },
            "u2": {
                "id": uuid.uuid5(uuid.NAMESPACE_DNS, "bdd-user:u2"),
                "role": "USER",
                "password": self.USER_PASSWORD,
            },
            "u3": {
                "id": uuid.uuid5(uuid.NAMESPACE_DNS, "bdd-user:u3"),
                "role": "USER",
                "password": self.USER_PASSWORD,
            },
            "admin-1": {
                "id": uuid.uuid5(uuid.NAMESPACE_DNS, "bdd-user:admin-1"),
                "role": "ADMIN",
                "password": self.USER_PASSWORD,
            },
            "viewer-1": {
                "id": uuid.uuid5(uuid.NAMESPACE_DNS, "bdd-user:viewer-1"),
                "role": "USER",
                "password": self.USER_PASSWORD,
            },
        }
        now = datetime.now(tz=UTC)

        insert_user_sql = text(
            """
            INSERT INTO users (id, username, password_hash, role, is_active)
            VALUES (:id, :username, :password_hash, :role, true)
            """
        )
        insert_template_sql = text(
            """
            INSERT INTO survey_templates (id, name, created_at, updated_at)
            VALUES (:id, :name, :created_at, :updated_at)
            """
        )
        insert_template_version_sql = text(
            """
            INSERT INTO survey_template_versions (id, template_id, version, is_published, created_at)
            VALUES (:id, :template_id, :version, :is_published, :created_at)
            """
        )
        insert_question_sql = text(
            """
            INSERT INTO survey_template_questions
                (id, template_version_id, key, title, question_type, required, order_no)
            VALUES
                (:id, :template_version_id, :key, :title, :question_type, :required, :order_no)
            """
        )
        insert_assignment_sql = text(
            """
            INSERT INTO survey_assignments
                (id, template_version_id, status, due_at, created_by, created_at, closed_at)
            VALUES
                (:id, :template_version_id, :status, :due_at, :created_by, :created_at, :closed_at)
            """
        )
        insert_assignee_sql = text(
            """
            INSERT INTO survey_assignment_assignees (id, assignment_id, assignee_user_id, submitted_at)
            VALUES (:id, :assignment_id, :assignee_user_id, :submitted_at)
            """
        )
        insert_submission_sql = text(
            """
            INSERT INTO survey_submissions (id, assignment_id, assignee_user_id, submitted_at)
            VALUES (:id, :assignment_id, :assignee_user_id, :submitted_at)
            """
        )
        insert_submission_answer_sql = text(
            """
            INSERT INTO survey_submission_answers (id, submission_id, question_key, answer_value, order_no)
            VALUES (:id, :submission_id, :question_key, :answer_value, :order_no)
            """
        )
        insert_audit_sql = text(
            """
            INSERT INTO survey_result_access_audits (id, actor_user_id, assignment_id, action, occurred_at)
            VALUES (:id, :actor_user_id, :assignment_id, :action, :occurred_at)
            """
        )

        with self._engine.begin() as connection:
            for username, user in users.items():
                connection.execute(
                    insert_user_sql,
                    {
                        "id": user["id"],
                        "username": username,
                        "password_hash": self._hash_password(user["password"]),
                        "role": user["role"],
                    },
                )

            required_survey_tables = (
                "survey_templates",
                "survey_template_versions",
                "survey_template_questions",
                "survey_assignments",
                "survey_assignment_assignees",
                "survey_submissions",
                "survey_submission_answers",
                "survey_result_access_audits",
            )
            if not all(self._table_exists(connection, table) for table in required_survey_tables):
                return

            connection.execute(
                insert_template_sql,
                {
                    "id": self.TEMPLATE_ID,
                    "name": "BDD Editable Template",
                    "created_at": now,
                    "updated_at": now,
                },
            )
            connection.execute(
                insert_template_sql,
                {
                    "id": self.PUBLISHED_TEMPLATE_ID,
                    "name": "BDD Baseline Template",
                    "created_at": now,
                    "updated_at": now,
                },
            )
            connection.execute(
                insert_template_version_sql,
                {
                    "id": self.TEMPLATE_VERSION_ID,
                    "template_id": self.PUBLISHED_TEMPLATE_ID,
                    "version": 1,
                    "is_published": True,
                    "created_at": now,
                },
            )

            role_question_id = uuid.uuid5(uuid.NAMESPACE_DNS, "bdd-question:role")
            connection.execute(
                insert_question_sql,
                {
                    "id": role_question_id,
                    "template_version_id": self.TEMPLATE_VERSION_ID,
                    "key": "role",
                    "title": "Role",
                    "question_type": "single_choice",
                    "required": True,
                    "order_no": 1,
                },
            )

            connection.execute(
                insert_assignment_sql,
                {
                    "id": self.ASSIGNMENT_ID,
                    "template_version_id": self.TEMPLATE_VERSION_ID,
                    "status": "in_progress",
                    "due_at": None,
                    "created_by": users[self.ADMIN_USERNAME]["id"],
                    "created_at": now,
                    "closed_at": None,
                },
            )

            for index, username in enumerate(("u1", "u2", "u3"), start=1):
                connection.execute(
                    insert_assignee_sql,
                    {
                        "id": uuid.uuid5(uuid.NAMESPACE_DNS, f"bdd-assignee:{username}"),
                        "assignment_id": self.ASSIGNMENT_ID,
                        "assignee_user_id": users[username]["id"],
                        "submitted_at": None,
                    },
                )

            submission_id = uuid.uuid5(uuid.NAMESPACE_DNS, "bdd-submission:u1")
            connection.execute(
                insert_submission_sql,
                {
                    "id": submission_id,
                    "assignment_id": self.ASSIGNMENT_ID,
                    "assignee_user_id": users["u1"]["id"],
                    "submitted_at": now,
                },
            )
            connection.execute(
                insert_submission_answer_sql,
                {
                    "id": uuid.uuid5(uuid.NAMESPACE_DNS, "bdd-answer:u1-role"),
                    "submission_id": submission_id,
                    "question_key": "role",
                    "answer_value": '"dev"',
                    "order_no": 1,
                },
            )
            connection.execute(
                insert_audit_sql,
                {
                    "id": uuid.uuid5(uuid.NAMESPACE_DNS, "bdd-audit:detail-view"),
                    "actor_user_id": users["admin-1"]["id"],
                    "assignment_id": self.ASSIGNMENT_ID,
                    "action": "survey_result_detail_view",
                    "occurred_at": now,
                },
            )

    @staticmethod
    def _table_exists(connection, table_name: str) -> bool:
        result = connection.execute(
            text(
                """
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = :table_name
                LIMIT 1
                """,
            ),
            {"table_name": table_name},
        ).scalar()
        return bool(result)

    def bootstrap_auth_cookie(self) -> dict[str, str]:
        admin_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"bdd-admin:{self.ADMIN_USERNAME}")
        auth_session_id = f"bdd-session-{uuid.uuid4()}"
        now = datetime.now(tz=UTC)
        expiration = now + self._settings.security.auth.session_ttl_min

        insert_session_sql = text(
            """
            INSERT INTO auth_sessions (id, user_id, expiration)
            VALUES (:id, :user_id, :expiration)
            """
        )
        with self._engine.begin() as connection:
            connection.execute(
                insert_session_sql,
                {
                    "id": auth_session_id,
                    "user_id": admin_id,
                    "expiration": expiration,
                },
            )

        access_token = jwt.encode(
            {
                "auth_session_id": auth_session_id,
                "exp": int(expiration.timestamp()),
            },
            key=self._settings.security.auth.jwt_secret,
            algorithm=self._settings.security.auth.jwt_algorithm,
        )
        return {"access_token": access_token}

    def baseline_state(self) -> dict[str, str]:
        user_ids = {
            "u1": str(uuid.uuid5(uuid.NAMESPACE_DNS, "bdd-user:u1")),
            "u2": str(uuid.uuid5(uuid.NAMESPACE_DNS, "bdd-user:u2")),
            "u3": str(uuid.uuid5(uuid.NAMESPACE_DNS, "bdd-user:u3")),
            "admin-1": str(uuid.uuid5(uuid.NAMESPACE_DNS, "bdd-user:admin-1")),
            "viewer-1": str(uuid.uuid5(uuid.NAMESPACE_DNS, "bdd-user:viewer-1")),
        }
        return {
            "template_id": str(self.TEMPLATE_ID),
            "template_version_id": str(self.TEMPLATE_VERSION_ID),
            "assignment_id": str(self.ASSIGNMENT_ID),
            "user_ids": user_ids,
        }

    def _hash_password(self, raw_password: str) -> bytes:
        peppered = self._add_pepper(raw_password, self._settings.security.password.pepper.encode())
        salt = bcrypt.gensalt(rounds=self._settings.security.password.hasher_work_factor)
        return bcrypt.hashpw(peppered, salt)

    @staticmethod
    def _add_pepper(raw_password: str, pepper: bytes) -> bytes:
        hmac_password = hmac.new(
            key=pepper,
            msg=raw_password.encode(),
            digestmod=hashlib.sha384,
        ).digest()
        return base64.b64encode(hmac_password)
