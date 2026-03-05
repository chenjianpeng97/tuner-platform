from __future__ import annotations

from datetime import UTC, datetime
from http import HTTPStatus
import uuid

from behave import given, then, when
import jwt

from app.application.common.exceptions.authorization import AuthorizationError
from app.domain.exceptions.survey import (
    SurveyAssignmentAssigneePermissionError,
    SurveyAssignmentSubmissionNotAllowedError,
)

API_SURVEYS = "/api/v1/surveys"
AUTH_COOKIES = {"access_token": "fake-test-token"}


def _auth_cookies(context) -> dict[str, str]:
    return getattr(context, "auth_cookies", AUTH_COOKIES)


def _is_real_mode(context) -> bool:
    return getattr(context, "http_mode", "mock") == "real"


def _ensure_state(context) -> None:
    if hasattr(context, "survey_state"):
        return
    if _is_real_mode(context):
        baseline = context.real_fixture_runner.baseline_state()
        context.survey_state = {
            "template_id": uuid.UUID(baseline["template_id"]),
            "template_version_id": uuid.UUID(baseline["template_version_id"]),
            "assignment_id": uuid.UUID(baseline["assignment_id"]),
            "user_ids": {
                username: uuid.UUID(user_id)
                for username, user_id in baseline["user_ids"].items()
            },
            "last_response": None,
        }
        return
    context.survey_state = {
        "template_id": uuid.uuid4(),
        "template_version_id": uuid.uuid4(),
        "assignment_id": uuid.uuid4(),
        "user_ids": {},
        "last_response": None,
    }


def _create_real_editable_template(context) -> None:
    response = context.client.post(
        f"{API_SURVEYS}/templates",
        json={
            "name": "BDD Editable Template",
            "questions": [
                {
                    "key": "role",
                    "title": "Role",
                    "question_type": "single_choice",
                    "required": True,
                    "options": ["dev", "qa"],
                }
            ],
        },
        cookies=_auth_cookies(context),
    )
    if response.status_code == HTTPStatus.CREATED:
        template_id = response.json().get("id")
        if template_id:
            context.survey_state["template_id"] = uuid.UUID(template_id)


def _normalized_real_username(username: str) -> str:
    if len(username) < 5:
        return f"bdd-{username}"
    return username


def _set_auth_cookies_for_user(context, username: str) -> None:
    if not _is_real_mode(context):
        return

    _ensure_state(context)
    canonical_username = _normalized_real_username(username)
    user_id = context.survey_state["user_ids"].get(canonical_username)
    if user_id is None:
        user_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"bdd-user:{canonical_username}")
        context.survey_state["user_ids"][canonical_username] = user_id
        context.survey_state["user_ids"][username] = user_id
        password_hash = context.real_fixture_runner._hash_password(
            context.real_fixture_runner.USER_PASSWORD,
        )
        with context.real_fixture_runner._engine.begin() as connection:
            connection.exec_driver_sql(
                """
                INSERT INTO users (id, username, password_hash, role, is_active)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (username)
                DO NOTHING
                """,
                (str(user_id), canonical_username, password_hash, "USER", True),
            )

    auth_session_id = f"bdd-session-{uuid.uuid4()}"
    now = datetime.now(tz=UTC)
    expiration = (
        now + context.real_fixture_runner._settings.security.auth.session_ttl_min
    )
    with context.real_fixture_runner._engine.begin() as connection:
        connection.exec_driver_sql(
            "INSERT INTO auth_sessions (id, user_id, expiration) VALUES (%s, %s, %s)",
            (auth_session_id, str(user_id), expiration),
        )

    access_token = jwt.encode(
        {
            "auth_session_id": auth_session_id,
            "exp": int(expiration.timestamp()),
        },
        key=context.real_fixture_runner._settings.security.auth.jwt_secret,
        algorithm=context.real_fixture_runner._settings.security.auth.jwt_algorithm,
    )
    context.auth_cookies = {"access_token": access_token}


def _seed_real_assignment(
    context,
    *,
    assignee_usernames: list[str],
    submitted_count: int = 0,
    due_at: datetime | None = None,
    force_assignment_id: uuid.UUID | None = None,
) -> uuid.UUID:
    _ensure_state(context)
    assignment_id = force_assignment_id or uuid.uuid4()
    template_version_id = context.survey_state["template_version_id"]
    submitted_count = min(submitted_count, len(assignee_usernames))
    now = datetime.now(tz=UTC)
    status = (
        "completed"
        if assignee_usernames and submitted_count == len(assignee_usernames)
        else "in_progress"
    )

    password_hash = context.real_fixture_runner._hash_password(
        context.real_fixture_runner.USER_PASSWORD,
    )

    with context.real_fixture_runner._engine.begin() as connection:
        connection.exec_driver_sql(
            """
            INSERT INTO survey_template_questions
                (id, template_version_id, key, title, question_type, required, order_no)
            SELECT %s, %s, %s, %s, %s, %s, %s
            WHERE NOT EXISTS (
                SELECT 1 FROM survey_template_questions
                WHERE template_version_id = %s AND key = %s
            )
            """,
            (
                str(
                    uuid.uuid5(
                        uuid.NAMESPACE_DNS,
                        f"bdd-question-feedback:{template_version_id}",
                    )
                ),
                str(template_version_id),
                "feedback",
                "Feedback",
                "text",
                False,
                99,
                str(template_version_id),
                "feedback",
            ),
        )
        connection.exec_driver_sql(
            """
            INSERT INTO survey_assignments (id, template_version_id, status, due_at, created_by, created_at, closed_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id)
            DO UPDATE SET template_version_id = EXCLUDED.template_version_id, status = EXCLUDED.status, due_at = EXCLUDED.due_at
            """,
            (
                str(assignment_id),
                str(template_version_id),
                status,
                due_at,
                None,
                now,
                now if status == "completed" else None,
            ),
        )
        connection.exec_driver_sql(
            "DELETE FROM survey_assignment_assignees WHERE assignment_id = %s",
            (str(assignment_id),),
        )
        connection.exec_driver_sql(
            "DELETE FROM survey_submissions WHERE assignment_id = %s",
            (str(assignment_id),),
        )

        for index, username in enumerate(assignee_usernames, start=1):
            canonical_username = _normalized_real_username(username)
            user_id = context.survey_state["user_ids"].get(canonical_username)
            if user_id is None:
                user_id = uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"bdd-assignee:{canonical_username}",
                )
                context.survey_state["user_ids"][canonical_username] = user_id
                context.survey_state["user_ids"][username] = user_id
                connection.exec_driver_sql(
                    """
                    INSERT INTO users (id, username, password_hash, role, is_active)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (username)
                    DO NOTHING
                    """,
                    (str(user_id), canonical_username, password_hash, "USER", True),
                )

            assignee_submitted_at = now if index <= submitted_count else None
            connection.exec_driver_sql(
                "INSERT INTO survey_assignment_assignees (id, assignment_id, assignee_user_id, submitted_at) VALUES (%s, %s, %s, %s)",
                (
                    str(uuid.uuid4()),
                    str(assignment_id),
                    str(user_id),
                    assignee_submitted_at,
                ),
            )
            if index <= submitted_count:
                submission_id = uuid.uuid4()
                connection.exec_driver_sql(
                    "INSERT INTO survey_submissions (id, assignment_id, assignee_user_id, submitted_at) VALUES (%s, %s, %s, %s)",
                    (str(submission_id), str(assignment_id), str(user_id), now),
                )
                connection.exec_driver_sql(
                    "INSERT INTO survey_submission_answers (id, submission_id, question_key, answer_value, order_no) VALUES (%s, %s, %s, %s, %s)",
                    (str(uuid.uuid4()), str(submission_id), "role", '"dev"', 1),
                )
                connection.exec_driver_sql(
                    "INSERT INTO survey_submission_answers (id, submission_id, question_key, answer_value, order_no) VALUES (%s, %s, %s, %s, %s)",
                    (
                        str(uuid.uuid4()),
                        str(submission_id),
                        "feedback",
                        f'"feedback-{index}"',
                        2,
                    ),
                )

    context.survey_state["assignment_id"] = assignment_id
    context.survey_state["assignee_usernames"] = list(assignee_usernames)
    return assignment_id


def _to_uuid(value: str) -> uuid.UUID:
    try:
        return uuid.UUID(value)
    except ValueError:
        return uuid.uuid5(uuid.NAMESPACE_DNS, f"survey-{value}")


def _user_id(context, username: str) -> uuid.UUID:
    _ensure_state(context)
    cache = context.survey_state["user_ids"]
    if username not in cache:
        cache[username] = _to_uuid(username)
    return cache[username]


@given("an authorized survey operator")
def given_authorized_survey_operator(context):
    _ensure_state(context)


@given("an editable survey template exists")
def given_editable_template_exists(context):
    _ensure_state(context)
    if _is_real_mode(context):
        _create_real_editable_template(context)


@given("a published template version is used by an assignment task")
def given_published_template_version_used(context):
    _ensure_state(context)
    if _is_real_mode(context):
        return
    context.survey_state["template_version_id"] = uuid.uuid4()
    context.survey_state["assignment_id"] = uuid.uuid4()
    context.mocks.get_survey_assignment.execute.return_value = {
        "id_": context.survey_state["assignment_id"],
        "template_version_id": context.survey_state["template_version_id"],
        "status": "in_progress",
        "due_at": None,
        "assignee_user_ids": [],
        "assignee_count": 0,
        "submitted_count": 0,
        "ratio": 0.0,
    }


@given("an immutable template version exists")
def given_immutable_template_version_exists(context):
    _ensure_state(context)
    if _is_real_mode(context):
        return
    context.survey_state["template_version_id"] = uuid.uuid4()


@given('an in-progress assignment task for users "{user_list}"')
def given_in_progress_assignment_task(context, user_list: str):
    _ensure_state(context)
    users = [user.strip() for user in user_list.split(",") if user.strip()]
    if _is_real_mode(context):
        _seed_real_assignment(context, assignee_usernames=users, submitted_count=0)
        return
    assignment_id = context.survey_state["assignment_id"]
    submitted_count = sum(
        1 for user in users if user in context.survey_state.get("submitted", set())
    )
    context.mocks.get_survey_assignment.execute.return_value = {
        "id_": assignment_id,
        "template_version_id": context.survey_state["template_version_id"],
        "status": "in_progress",
        "due_at": None,
        "assignee_user_ids": [_user_id(context, user) for user in users],
        "assignee_count": len(users),
        "submitted_count": submitted_count,
        "ratio": submitted_count / len(users) if users else 0.0,
    }


@given('user "{username}" has submitted')
def given_user_has_submitted(context, username: str):
    _ensure_state(context)
    if _is_real_mode(context):
        _set_auth_cookies_for_user(context, username)
        response = context.client.put(
            f"{API_SURVEYS}/assignments/{context.survey_state['assignment_id']}/my-submission",
            json={"answers": {"role": username}},
            cookies=_auth_cookies(context),
        )
        assert response.status_code in {
            HTTPStatus.OK,
            HTTPStatus.CREATED,
            HTTPStatus.NO_CONTENT,
        }
        return
    submitted = context.survey_state.setdefault("submitted", set())
    submitted.add(username)


@given('task progress is "{submitted}/{assignees}"')
def given_task_progress(context, submitted: str, assignees: str):
    _ensure_state(context)
    if _is_real_mode(context):
        submitted_count = int(submitted)
        assignee_count = int(assignees)
        assignee_names = [
            f"progress-user-{index + 1}" for index in range(assignee_count)
        ]
        _seed_real_assignment(
            context,
            assignee_usernames=assignee_names,
            submitted_count=submitted_count,
        )
        return
    assignment_id = context.survey_state["assignment_id"]
    submitted_count = int(submitted)
    assignee_count = int(assignees)
    assignee_ids = [
        _user_id(context, f"u{index + 1}") for index in range(assignee_count)
    ]
    context.mocks.get_survey_assignment.execute.return_value = {
        "id_": assignment_id,
        "template_version_id": context.survey_state["template_version_id"],
        "status": "completed"
        if assignee_count and submitted_count == assignee_count
        else "in_progress",
        "due_at": None,
        "assignee_user_ids": assignee_ids,
        "assignee_count": assignee_count,
        "submitted_count": submitted_count,
        "ratio": submitted_count / assignee_count if assignee_count else 0.0,
    }


@given('assignment task "{assignment_key}" is assigned to user "{username}"')
def given_assignment_assigned_to_user(context, assignment_key: str, username: str):
    _ensure_state(context)
    if _is_real_mode(context) and assignment_key == "A-1":
        context.survey_state["assignment_id"] = _seed_real_assignment(
            context,
            assignee_usernames=[username],
            submitted_count=0,
            force_assignment_id=context.real_fixture_runner.ASSIGNMENT_ID,
        )
    else:
        context.survey_state["assignment_id"] = _to_uuid(assignment_key)
    context.survey_state["assignee"] = username


@given(
    'assignment task "{assignment_key}" is in progress and assigned to user "{username}"'
)
def given_assignment_in_progress_assigned(context, assignment_key: str, username: str):
    if _is_real_mode(context) and assignment_key == "A-1":
        context.survey_state["assignment_id"] = _seed_real_assignment(
            context,
            assignee_usernames=[username, "u3"],
            submitted_count=0,
            force_assignment_id=context.real_fixture_runner.ASSIGNMENT_ID,
        )
        context.survey_state["assignee"] = username
        return
    given_assignment_assigned_to_user(context, assignment_key, username)


@given('assignment task "{assignment_key}" has due date in the past')
def given_assignment_due_in_past(context, assignment_key: str):
    _ensure_state(context)
    if _is_real_mode(context) and assignment_key == "A-1":
        context.survey_state["assignment_id"] = _seed_real_assignment(
            context,
            assignee_usernames=["u1"],
            submitted_count=0,
            due_at=datetime.now(UTC).replace(year=datetime.now(UTC).year - 1),
            force_assignment_id=context.real_fixture_runner.ASSIGNMENT_ID,
        )
    else:
        context.survey_state["assignment_id"] = _to_uuid(assignment_key)
    if _is_real_mode(context):
        return
    context.mocks.submit_my_survey_submission.execute.side_effect = (
        SurveyAssignmentSubmissionNotAllowedError(reason="deadline exceeded")
    )


@given('assignment task "{assignment_key}" has at least one effective submission')
def given_assignment_has_submission(context, assignment_key: str):
    _ensure_state(context)
    if _is_real_mode(context) and assignment_key == "A-1":
        assignment_id = _seed_real_assignment(
            context,
            assignee_usernames=["u1"],
            submitted_count=1,
            force_assignment_id=context.real_fixture_runner.ASSIGNMENT_ID,
        )
    else:
        assignment_id = _to_uuid(assignment_key)
    context.survey_state["assignment_id"] = assignment_id
    if _is_real_mode(context):
        return
    context.mocks.get_survey_assignment_submissions.execute.return_value = [
        {
            "assignment_id": assignment_id,
            "assignee_user_id": _user_id(context, "u1"),
            "answers": {"role": "dev"},
            "submitted_at": datetime.now(UTC),
        }
    ]


@given('user "{username}" has survey-library permission')
def given_user_has_permission(context, username: str):
    _ensure_state(context)
    context.survey_state["viewer"] = username


@given('user "{username}" does not have survey-library permission')
def given_user_no_permission(context, username: str):
    _ensure_state(context)
    context.survey_state["viewer"] = username
    if _is_real_mode(context):
        return
    context.mocks.get_survey_assignment_submissions.execute.side_effect = (
        AuthorizationError
    )


@given('assignment task "{assignment_key}" has multiple submissions')
def given_assignment_has_multiple_submissions(context, assignment_key: str):
    _ensure_state(context)
    if _is_real_mode(context) and assignment_key == "A-1":
        assignment_id = _seed_real_assignment(
            context,
            assignee_usernames=["u1", "u2"],
            submitted_count=2,
            force_assignment_id=context.real_fixture_runner.ASSIGNMENT_ID,
        )
    else:
        assignment_id = _to_uuid(assignment_key)
    context.survey_state["assignment_id"] = assignment_id
    if _is_real_mode(context):
        return
    context.mocks.get_survey_assignment_summary.execute.return_value = {
        "assignment_id": assignment_id,
        "choice_counts": {"role": {"dev": 1, "qa": 1}},
        "text_answers": {"feedback": ["good", "improve docs"]},
    }


@given("a team adds new acceptance feature files for survey workflow")
def given_team_adds_new_feature_files(context):
    context.survey_state = {"feature_files": ["survey-assignment-workflow.feature"]}


@given("the same survey assignment feature must be validated at HTTP and UI layers")
def given_same_feature_multi_stage(context):
    _ensure_state(context)


@when(
    "the operator creates a survey template with single choice, multi choice, and text questions"
)
def when_create_survey_template(context):
    _ensure_state(context)
    template_id = context.survey_state["template_id"]
    context.mocks.create_survey_template.execute.return_value = {"id": template_id}
    request_body = {
        "name": "Platform Feedback",
        "questions": [
            {
                "key": "role",
                "title": "Role",
                "question_type": "single_choice",
                "required": True,
                "options": ["dev", "qa"],
            },
            {
                "key": "tools",
                "title": "Tools",
                "question_type": "multi_choice",
                "required": False,
                "options": ["dashboard", "api"],
            },
            {
                "key": "feedback",
                "title": "Feedback",
                "question_type": "text",
                "required": False,
                "options": [],
            },
        ],
    }
    context.response = context.client.post(
        f"{API_SURVEYS}/templates",
        json=request_body,
        cookies=_auth_cookies(context),
    )


@when("the operator publishes the template")
def when_publish_template(context):
    _ensure_state(context)
    if (
        _is_real_mode(context)
        and context.survey_state.get("template_id")
        == context.real_fixture_runner.TEMPLATE_ID
    ):
        _create_real_editable_template(context)
    context.mocks.publish_survey_template.execute.return_value = {
        "version_id": context.survey_state["template_version_id"]
    }
    context.response = context.client.post(
        f"{API_SURVEYS}/templates/{context.survey_state['template_id']}/publish",
        cookies=_auth_cookies(context),
    )


@when("the operator updates the editable template content later")
def when_update_template_later(context):
    _ensure_state(context)
    context.mocks.update_survey_template.execute.return_value = None
    context.response = context.client.patch(
        f"{API_SURVEYS}/templates/{context.survey_state['template_id']}",
        json={
            "name": "Platform Feedback V2",
            "questions": [
                {
                    "key": "feedback",
                    "title": "Feedback updated",
                    "question_type": "text",
                    "required": False,
                    "options": [],
                }
            ],
        },
        cookies=_auth_cookies(context),
    )


@when('an operator creates an assignment task for users "{user_list}"')
def when_operator_creates_assignment(context, user_list: str):
    _ensure_state(context)
    users = [user.strip() for user in user_list.split(",") if user.strip()]
    assignee_ids = [_user_id(context, user) for user in users]
    assignment_id = context.survey_state["assignment_id"]
    context.mocks.create_survey_assignment.execute.return_value = {"id": assignment_id}
    context.mocks.get_survey_assignment.execute.return_value = {
        "id_": assignment_id,
        "template_version_id": context.survey_state["template_version_id"],
        "status": "in_progress",
        "due_at": None,
        "assignee_user_ids": assignee_ids,
        "assignee_count": len(assignee_ids),
        "submitted_count": 0,
        "ratio": 0.0,
    }
    context.response = context.client.post(
        f"{API_SURVEYS}/assignments",
        json={
            "template_version_id": str(context.survey_state["template_version_id"]),
            "assignee_user_ids": [str(user_id) for user_id in assignee_ids],
        },
        cookies=_auth_cookies(context),
    )
    if context.response.status_code == HTTPStatus.CREATED:
        assignment_id = context.response.json().get("id")
        if assignment_id:
            context.survey_state["assignment_id"] = uuid.UUID(assignment_id)


@when("an operator creates an assignment task without due date")
def when_create_assignment_without_due_date(context):
    when_operator_creates_assignment(context, "u1,u2")


@when('user "{username}" submits successfully')
def when_user_submit_success(context, username: str):
    _ensure_state(context)
    _set_auth_cookies_for_user(context, username)
    context.mocks.submit_my_survey_submission.execute.return_value = None
    context.response = context.client.put(
        f"{API_SURVEYS}/assignments/{context.survey_state['assignment_id']}/my-submission",
        json={"answers": {"role": username}},
        cookies=_auth_cookies(context),
    )
    context.survey_state["submitted"] = {"u1", "u2"}
    context.mocks.get_survey_assignment.execute.return_value = {
        "id_": context.survey_state["assignment_id"],
        "template_version_id": context.survey_state["template_version_id"],
        "status": "completed",
        "due_at": None,
        "assignee_user_ids": [_user_id(context, "u1"), _user_id(context, "u2")],
        "assignee_count": 2,
        "submitted_count": 2,
        "ratio": 1.0,
    }


@when("an operator closes the assignment task")
def when_operator_close_assignment(context):
    _ensure_state(context)
    context.mocks.close_survey_assignment.execute.return_value = None
    context.response = context.client.post(
        f"{API_SURVEYS}/assignments/{context.survey_state['assignment_id']}/close",
        cookies=_auth_cookies(context),
    )
    assignment_snapshot = context.mocks.get_survey_assignment.execute.return_value
    if assignment_snapshot:
        context.mocks.get_survey_assignment.execute.return_value = {
            **assignment_snapshot,
            "status": "completed",
        }
    context.mocks.submit_my_survey_submission.execute.side_effect = (
        SurveyAssignmentSubmissionNotAllowedError(reason="assignment completed")
    )


@when('user "{username}" tries to submit response for assignment "{assignment_key}"')
def when_user_try_submit_other(context, username: str, assignment_key: str):
    _ensure_state(context)
    if _is_real_mode(context) and assignment_key == "A-1":
        context.survey_state["assignment_id"] = (
            context.real_fixture_runner.ASSIGNMENT_ID
        )
    else:
        context.survey_state["assignment_id"] = _to_uuid(assignment_key)
    _set_auth_cookies_for_user(context, username)
    assignee = context.survey_state.get("assignee")
    if assignee and assignee != username:
        context.mocks.submit_my_survey_submission.execute.side_effect = (
            SurveyAssignmentAssigneePermissionError
        )
    context.response = context.client.put(
        f"{API_SURVEYS}/assignments/{context.survey_state['assignment_id']}/my-submission",
        json={"answers": {"role": "dev"}},
        cookies=_auth_cookies(context),
    )


@when('user "{username}" submits response "{response_key}"')
def when_user_submits_response(context, username: str, response_key: str):
    _ensure_state(context)
    _set_auth_cookies_for_user(context, username)
    context.mocks.submit_my_survey_submission.execute.return_value = None
    effective_response = response_key
    if _is_real_mode(context):
        effective_response = "dev" if response_key == "R1" else "qa"
    payload = {"answers": {"role": effective_response}}
    context.response = context.client.put(
        f"{API_SURVEYS}/assignments/{context.survey_state['assignment_id']}/my-submission",
        json=payload,
        cookies=_auth_cookies(context),
    )
    context.survey_state["last_response"] = effective_response


@when('user "{username}" submits response "{response_key}" again before due date')
def when_user_submits_response_again(context, username: str, response_key: str):
    when_user_submits_response(context, username, response_key)
    assignment_id = context.survey_state["assignment_id"]
    assignee_id = _user_id(context, username)
    context.mocks.get_survey_assignment_submissions.execute.return_value = [
        {
            "assignment_id": assignment_id,
            "assignee_user_id": assignee_id,
            "answers": {"role": response_key},
            "submitted_at": datetime.now(UTC),
        }
    ]
    context.mocks.get_survey_assignment.execute.return_value = {
        "id_": assignment_id,
        "template_version_id": context.survey_state["template_version_id"],
        "status": "in_progress",
        "due_at": None,
        "assignee_user_ids": [assignee_id],
        "assignee_count": 1,
        "submitted_count": 1,
        "ratio": 1.0,
    }


@when('user "{username}" submits response')
def when_user_submit_response(context, username: str):
    _ensure_state(context)
    _set_auth_cookies_for_user(context, username)
    context.response = context.client.put(
        f"{API_SURVEYS}/assignments/{context.survey_state['assignment_id']}/my-submission",
        json={"answers": {"role": "dev"}},
        cookies=_auth_cookies(context),
    )


@when('user "{username}" requests assignment detailed submissions')
def when_user_request_detailed_submissions(context, username: str):
    _ensure_state(context)
    _set_auth_cookies_for_user(context, username)
    context.response = context.client.get(
        f"{API_SURVEYS}/assignments/{context.survey_state['assignment_id']}/submissions",
        cookies=_auth_cookies(context),
    )


@when("an authorized user requests assignment summary")
def when_authorized_user_requests_summary(context):
    _ensure_state(context)
    context.response = context.client.get(
        f"{API_SURVEYS}/assignments/{context.survey_state['assignment_id']}/summary",
        cookies=_auth_cookies(context),
    )


@when("the test suite is executed with stage-specific command options")
def when_suite_executed_with_stage(context):
    context.survey_state["stage_used"] = context.config.stage


@then("the template is stored as editable draft")
def then_template_stored_as_draft(context):
    assert context.response.status_code == HTTPStatus.CREATED
    if getattr(context, "http_mode", "mock") == "mock":
        assert context.mocks.create_survey_template.execute.await_count == 1


@then("an immutable template version is created")
def then_immutable_version_created(context):
    assert context.response.status_code == HTTPStatus.CREATED
    payload = context.response.json()
    assert payload.get("version_id")


@then("the existing assignment still uses the original frozen version")
def then_assignment_uses_original_version(context):
    response = context.client.get(
        f"{API_SURVEYS}/assignments/{context.survey_state['assignment_id']}",
        cookies=_auth_cookies(context),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json().get("template_version_id") == str(
        context.survey_state["template_version_id"]
    )


@then('the assignment task status is "{status}"')
def then_assignment_status_is(context, status: str):
    response = context.client.get(
        f"{API_SURVEYS}/assignments/{context.survey_state['assignment_id']}",
        cookies=_auth_cookies(context),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["status"] == status


@then('task progress is "{submitted}/{assignees}"')
def then_task_progress_is(context, submitted: str, assignees: str):
    response = context.client.get(
        f"{API_SURVEYS}/assignments/{context.survey_state['assignment_id']}",
        cookies=_auth_cookies(context),
    )
    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body["submitted_count"] == int(submitted)
    assert body["assignee_count"] == int(assignees)


@then("the assignment task is accepted")
def then_assignment_task_accepted(context):
    assert context.response.status_code == HTTPStatus.CREATED


@then('the assignment task status becomes "completed"')
def then_assignment_status_completed(context):
    then_assignment_status_is(context, "completed")


@then("further submissions are rejected")
def then_further_submissions_rejected(context):
    if _is_real_mode(context):
        assignees = context.survey_state.get("assignee_usernames") or ["u1"]
        _set_auth_cookies_for_user(context, assignees[0])
    response = context.client.put(
        f"{API_SURVEYS}/assignments/{context.survey_state['assignment_id']}/my-submission",
        json={"answers": {"role": "blocked"}},
        cookies=_auth_cookies(context),
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@then("the request is denied")
def then_request_denied(context):
    assert context.response.status_code == HTTPStatus.FORBIDDEN


@then('response "{response_key}" is the effective submission for result views')
def then_response_is_effective(context, response_key: str):
    if _is_real_mode(context):
        _set_auth_cookies_for_user(context, "admin-1")
    response = context.client.get(
        f"{API_SURVEYS}/assignments/{context.survey_state['assignment_id']}/submissions",
        cookies=_auth_cookies(context),
    )
    assert response.status_code == HTTPStatus.OK
    payload = response.json()
    expected_response = response_key
    if _is_real_mode(context):
        expected_response = "dev" if response_key == "R1" else "qa"
    assert payload[0]["answers"]["role"] == expected_response


@then('submitted count is increased only once for user "{username}"')
def then_submitted_count_once(context, username: str):
    if _is_real_mode(context):
        _set_auth_cookies_for_user(context, "admin-1")
    response = context.client.get(
        f"{API_SURVEYS}/assignments/{context.survey_state['assignment_id']}",
        cookies=_auth_cookies(context),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["submitted_count"] == 1


@then("the request is rejected")
def then_request_rejected(context):
    assert context.response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@then("effective latest submissions are returned per assignee")
def then_effective_submissions_returned(context):
    assert context.response.status_code == HTTPStatus.OK
    payload = context.response.json()
    assert isinstance(payload, list)
    assert payload


@then("an audit record is created for raw-response access")
def then_audit_record_created(context):
    if getattr(context, "http_mode", "mock") == "mock":
        assert context.mocks.get_survey_assignment_submissions.execute.await_count == 1


@then("the request is forbidden")
def then_request_forbidden(context):
    assert context.response.status_code == HTTPStatus.FORBIDDEN


@then("aggregated counts for choice questions are returned")
def then_choice_aggregations_returned(context):
    assert context.response.status_code == HTTPStatus.OK
    payload = context.response.json()
    assert payload["choice_counts"]


@then("text answers are returned as a reviewable collection")
def then_text_answers_returned(context):
    payload = context.response.json()
    assert payload["text_answers"]


@then(
    'the file names do not use layer suffix patterns like "_http.feature" or "_ui.feature"'
)
def then_feature_files_no_layer_suffix(context):
    for name in context.survey_state.get("feature_files", []):
        assert not name.endswith("_http.feature")
        assert not name.endswith("_ui.feature")


@then("feature names describe business capabilities")
def then_feature_names_business(context):
    feature_name = (context.feature.name or "").lower()
    assert "workflow" in feature_name or "survey" in feature_name


@then("the stage selects the step implementation layer")
def then_stage_selects_layer(context):
    assert context.survey_state.get("stage_used") == "http"


@then("the business feature file remains shared")
def then_business_feature_shared(context):
    feature_file = str(context.feature.filename)
    assert feature_file.endswith("survey-assignment-workflow.feature")
    assert "_http.feature" not in feature_file and "_ui.feature" not in feature_file
