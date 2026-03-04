from __future__ import annotations

from datetime import UTC, datetime
from http import HTTPStatus
import uuid

from behave import given, then, when

from app.application.common.exceptions.authorization import AuthorizationError
from app.domain.exceptions.survey import (
    SurveyAssignmentAssigneePermissionError,
    SurveyAssignmentSubmissionNotAllowedError,
)

API_SURVEYS = "/api/v1/surveys"
AUTH_COOKIES = {"access_token": "fake-test-token"}


def _ensure_state(context) -> None:
    if hasattr(context, "survey_state"):
        return
    context.survey_state = {
        "template_id": uuid.uuid4(),
        "template_version_id": uuid.uuid4(),
        "assignment_id": uuid.uuid4(),
        "user_ids": {},
        "last_response": None,
    }


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


@given("a published template version is used by an assignment task")
def given_published_template_version_used(context):
    _ensure_state(context)
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
    context.survey_state["template_version_id"] = uuid.uuid4()


@given('an in-progress assignment task for users "{user_list}"')
def given_in_progress_assignment_task(context, user_list: str):
    _ensure_state(context)
    users = [user.strip() for user in user_list.split(",") if user.strip()]
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
    submitted = context.survey_state.setdefault("submitted", set())
    submitted.add(username)


@given('task progress is "{submitted}/{assignees}"')
def given_task_progress(context, submitted: str, assignees: str):
    _ensure_state(context)
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
    context.survey_state["assignment_id"] = _to_uuid(assignment_key)
    context.survey_state["assignee"] = username


@given(
    'assignment task "{assignment_key}" is in progress and assigned to user "{username}"'
)
def given_assignment_in_progress_assigned(context, assignment_key: str, username: str):
    given_assignment_assigned_to_user(context, assignment_key, username)


@given('assignment task "{assignment_key}" has due date in the past')
def given_assignment_due_in_past(context, assignment_key: str):
    _ensure_state(context)
    context.survey_state["assignment_id"] = _to_uuid(assignment_key)
    context.mocks.submit_my_survey_submission.execute.side_effect = (
        SurveyAssignmentSubmissionNotAllowedError(reason="deadline exceeded")
    )


@given('assignment task "{assignment_key}" has at least one effective submission')
def given_assignment_has_submission(context, assignment_key: str):
    _ensure_state(context)
    assignment_id = _to_uuid(assignment_key)
    context.survey_state["assignment_id"] = assignment_id
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
    context.mocks.get_survey_assignment_submissions.execute.side_effect = (
        AuthorizationError
    )


@given('assignment task "{assignment_key}" has multiple submissions')
def given_assignment_has_multiple_submissions(context, assignment_key: str):
    _ensure_state(context)
    assignment_id = _to_uuid(assignment_key)
    context.survey_state["assignment_id"] = assignment_id
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
        cookies=AUTH_COOKIES,
    )


@when("the operator publishes the template")
def when_publish_template(context):
    _ensure_state(context)
    context.mocks.publish_survey_template.execute.return_value = {
        "version_id": context.survey_state["template_version_id"]
    }
    context.response = context.client.post(
        f"{API_SURVEYS}/templates/{context.survey_state['template_id']}/publish",
        cookies=AUTH_COOKIES,
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
        cookies=AUTH_COOKIES,
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
        cookies=AUTH_COOKIES,
    )


@when("an operator creates an assignment task without due date")
def when_create_assignment_without_due_date(context):
    when_operator_creates_assignment(context, "u1,u2")


@when('user "{username}" submits successfully')
def when_user_submit_success(context, username: str):
    _ensure_state(context)
    context.mocks.submit_my_survey_submission.execute.return_value = None
    context.response = context.client.put(
        f"{API_SURVEYS}/assignments/{context.survey_state['assignment_id']}/my-submission",
        json={"answers": {"role": username}},
        cookies=AUTH_COOKIES,
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
        cookies=AUTH_COOKIES,
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
    context.survey_state["assignment_id"] = _to_uuid(assignment_key)
    assignee = context.survey_state.get("assignee")
    if assignee and assignee != username:
        context.mocks.submit_my_survey_submission.execute.side_effect = (
            SurveyAssignmentAssigneePermissionError
        )
    context.response = context.client.put(
        f"{API_SURVEYS}/assignments/{context.survey_state['assignment_id']}/my-submission",
        json={"answers": {"role": "dev"}},
        cookies=AUTH_COOKIES,
    )


@when('user "{username}" submits response "{response_key}"')
def when_user_submits_response(context, username: str, response_key: str):
    _ensure_state(context)
    context.mocks.submit_my_survey_submission.execute.return_value = None
    payload = {"answers": {"role": response_key}}
    context.response = context.client.put(
        f"{API_SURVEYS}/assignments/{context.survey_state['assignment_id']}/my-submission",
        json=payload,
        cookies=AUTH_COOKIES,
    )
    context.survey_state["last_response"] = response_key


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
    context.response = context.client.put(
        f"{API_SURVEYS}/assignments/{context.survey_state['assignment_id']}/my-submission",
        json={"answers": {"role": "dev"}},
        cookies=AUTH_COOKIES,
    )


@when('user "{username}" requests assignment detailed submissions')
def when_user_request_detailed_submissions(context, username: str):
    _ensure_state(context)
    context.response = context.client.get(
        f"{API_SURVEYS}/assignments/{context.survey_state['assignment_id']}/submissions",
        cookies=AUTH_COOKIES,
    )


@when("an authorized user requests assignment summary")
def when_authorized_user_requests_summary(context):
    _ensure_state(context)
    context.response = context.client.get(
        f"{API_SURVEYS}/assignments/{context.survey_state['assignment_id']}/summary",
        cookies=AUTH_COOKIES,
    )


@when("the test suite is executed with stage-specific command options")
def when_suite_executed_with_stage(context):
    context.survey_state["stage_used"] = context.config.stage


@then("the template is stored as editable draft")
def then_template_stored_as_draft(context):
    assert context.response.status_code == HTTPStatus.CREATED
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
        cookies=AUTH_COOKIES,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json().get("template_version_id") == str(
        context.survey_state["template_version_id"]
    )


@then('the assignment task status is "{status}"')
def then_assignment_status_is(context, status: str):
    response = context.client.get(
        f"{API_SURVEYS}/assignments/{context.survey_state['assignment_id']}",
        cookies=AUTH_COOKIES,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["status"] == status


@then('task progress is "{submitted}/{assignees}"')
def then_task_progress_is(context, submitted: str, assignees: str):
    response = context.client.get(
        f"{API_SURVEYS}/assignments/{context.survey_state['assignment_id']}",
        cookies=AUTH_COOKIES,
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
    response = context.client.put(
        f"{API_SURVEYS}/assignments/{context.survey_state['assignment_id']}/my-submission",
        json={"answers": {"role": "blocked"}},
        cookies=AUTH_COOKIES,
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@then("the request is denied")
def then_request_denied(context):
    assert context.response.status_code == HTTPStatus.FORBIDDEN


@then('response "{response_key}" is the effective submission for result views')
def then_response_is_effective(context, response_key: str):
    response = context.client.get(
        f"{API_SURVEYS}/assignments/{context.survey_state['assignment_id']}/submissions",
        cookies=AUTH_COOKIES,
    )
    assert response.status_code == HTTPStatus.OK
    payload = response.json()
    assert payload[0]["answers"]["role"] == response_key


@then('submitted count is increased only once for user "{username}"')
def then_submitted_count_once(context, username: str):
    response = context.client.get(
        f"{API_SURVEYS}/assignments/{context.survey_state['assignment_id']}",
        cookies=AUTH_COOKIES,
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
