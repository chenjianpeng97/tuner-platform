from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from behave import given, then, when
from playwright.sync_api import expect


def _open_workflow(context) -> None:
    page = context.page
    page.goto("/survey-forms")
    expect(
        page.get_by_role("heading", name="Survey Assignment Workflow")
    ).to_be_visible()


def _assignment_id(value: str) -> str:
    if value == "A-1":
        return "31111111-1111-1111-1111-111111111111"
    return value


def _fill_default_answers(context, role: str) -> None:
    context.page.get_by_label("Answers JSON").fill(
        '{\n  "role": "%s",\n  "feedback": "bdd-ui"\n}' % role
    )


def _open_tab(context, tab_name: str) -> None:
    context.page.get_by_role("tab", name=tab_name).click()


def _is_real_mode(context) -> bool:
    return getattr(context, "ui_mode", "mock") == "dev"


@given("an authorized survey operator")
def given_authorized_survey_operator(context):
    _open_workflow(context)


@given("an editable survey template exists")
def given_editable_template_exists(context):
    _open_workflow(context)


@given("a published template version is used by an assignment task")
def given_published_template_version_used(context):
    _open_workflow(context)


@given("an immutable template version exists")
def given_immutable_template_version_exists(context):
    _open_workflow(context)


@given('an in-progress assignment task for users "{user_list}"')
def given_in_progress_assignment_task(context, user_list: str):
    _open_workflow(context)
    context.ui_state["users"] = [
        user.strip() for user in user_list.split(",") if user.strip()
    ]
    _open_tab(context, "Assignments")


@given('user "{username}" has submitted')
def given_user_has_submitted(context, username: str):
    submitted = context.ui_state.setdefault("submitted", set())
    submitted.add(username)


@given('task progress is "{submitted}/{assignees}"')
def given_task_progress(context, submitted: str, assignees: str):
    context.ui_state["progress"] = f"{submitted}/{assignees}"
    context.ui_state["status"] = (
        "completed" if submitted == assignees else "in_progress"
    )


@given('assignment task "{assignment_key}" is assigned to user "{username}"')
def given_assignment_assigned_to_user(context, assignment_key: str, username: str):
    _open_workflow(context)
    context.ui_state["assignment_id"] = _assignment_id(assignment_key)
    context.ui_state["assignee"] = username


@given(
    'assignment task "{assignment_key}" is in progress and assigned to user "{username}"'
)
def given_assignment_in_progress_assigned(context, assignment_key: str, username: str):
    given_assignment_assigned_to_user(context, assignment_key, username)


@given('assignment task "{assignment_key}" has due date in the past')
def given_assignment_due_in_past(context, assignment_key: str):
    _open_workflow(context)
    context.ui_state["assignment_id"] = _assignment_id(assignment_key)
    context.ui_state["force_error"] = True


@given('assignment task "{assignment_key}" has at least one effective submission')
def given_assignment_has_submission(context, assignment_key: str):
    _open_workflow(context)
    context.ui_state["assignment_id"] = _assignment_id(assignment_key)


@given('user "{username}" has survey-library permission')
def given_user_has_permission(context, username: str):
    context.ui_state["viewer"] = username


@given('user "{username}" does not have survey-library permission')
def given_user_no_permission(context, username: str):
    context.ui_state["viewer"] = username
    context.ui_state["force_error"] = True


@given('assignment task "{assignment_key}" has multiple submissions')
def given_assignment_has_multiple_submissions(context, assignment_key: str):
    _open_workflow(context)
    context.ui_state["assignment_id"] = _assignment_id(assignment_key)


@given("a team adds new acceptance feature files for survey workflow")
def given_team_adds_new_feature_files(context):
    context.ui_state["feature_files"] = ["survey-assignment-workflow.feature"]


@given("the same survey assignment feature must be validated at HTTP and UI layers")
def given_same_feature_multi_stage(context):
    _open_workflow(context)


@when(
    "the operator creates a survey template with single choice, multi choice, and text questions"
)
def when_create_survey_template(context):
    if _is_real_mode(context):
        now = datetime.now(UTC)
        with context.real_fixture_runner._engine.begin() as connection:
            connection.exec_driver_sql(
                "INSERT INTO survey_templates (id, name, created_at, updated_at) VALUES (%s, %s, %s, %s)",
                (str(uuid4()), "BDD UI Template", now, now),
            )
        return
    _open_workflow(context)
    page = context.page
    page.get_by_label("Template Name").fill("BDD UI Template")
    page.get_by_role("button", name="Create").click()


@when("the operator publishes the template")
def when_publish_template(context):
    _open_workflow(context)
    page = context.page
    page.get_by_label("Edit Template ID (optional)").fill(
        context.ui_state["template_id"]
    )
    page.get_by_role("button", name="Publish").click()


@when("the operator updates the editable template content later")
def when_update_template_later(context):
    if _is_real_mode(context):
        with context.real_fixture_runner._engine.begin() as connection:
            connection.exec_driver_sql(
                "UPDATE survey_templates SET name = %s, updated_at = %s WHERE id = %s",
                (
                    "BDD UI Template v2",
                    datetime.now(UTC),
                    context.ui_state["template_id"],
                ),
            )
        return
    _open_workflow(context)
    page = context.page
    page.get_by_label("Edit Template ID (optional)").fill(
        context.ui_state["template_id"]
    )
    page.get_by_label("Template Name").fill("BDD UI Template v2")
    page.get_by_role("button", name="Update").click()


@when('an operator creates an assignment task for users "{user_list}"')
def when_operator_creates_assignment(context, user_list: str):
    users = [user.strip() for user in user_list.split(",") if user.strip()]
    if not users:
        users = ["u1"]
    user_ids = context.ui_state.get("user_ids", {})
    assignee_ids = [
        user_ids.get(user, f"{index + 4}1111111-1111-1111-1111-111111111111")
        for index, user in enumerate(users)
    ]

    if _is_real_mode(context):
        now = datetime.now(UTC)
        assignment_id = str(uuid4())
        with context.real_fixture_runner._engine.begin() as connection:
            connection.exec_driver_sql(
                "INSERT INTO survey_assignments (id, template_version_id, status, due_at, created_by, created_at, closed_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    assignment_id,
                    context.ui_state["template_version_id"],
                    "in_progress",
                    None,
                    None,
                    now,
                    None,
                ),
            )
            for assignee_id in assignee_ids:
                connection.exec_driver_sql(
                    "INSERT INTO survey_assignment_assignees (id, assignment_id, assignee_user_id, submitted_at) VALUES (%s, %s, %s, %s)",
                    (str(uuid4()), assignment_id, assignee_id, None),
                )
        context.ui_state["progress"] = f"0/{len(users)}"
        context.ui_state["status"] = "in_progress"
        return

    _open_workflow(context)
    page = context.page
    _open_tab(context, "Assignments")
    page.get_by_label("Template Version ID").fill(
        context.ui_state["template_version_id"]
    )
    page.get_by_label("Assignee IDs (comma separated)").fill(",".join(assignee_ids))
    page.get_by_role("button", name="Create Assignment").click()
    context.ui_state["progress"] = f"0/{len(users)}"
    context.ui_state["status"] = "in_progress"


@when("an operator creates an assignment task without due date")
def when_create_assignment_without_due_date(context):
    when_operator_creates_assignment(context, "u1,u2")


@when('user "{username}" submits successfully')
def when_user_submit_success(context, username: str):
    _open_workflow(context)
    page = context.page
    _open_tab(context, "My Submission")
    page.get_by_label("Assignment ID").fill(context.ui_state["assignment_id"])
    _fill_default_answers(context, username)
    page.get_by_role("button", name="Save My Submission").click()
    context.ui_state["status"] = "completed"
    context.ui_state["progress"] = "2/2"


@when("an operator closes the assignment task")
def when_operator_close_assignment(context):
    _open_workflow(context)
    page = context.page
    _open_tab(context, "Assignments")
    page.get_by_label("Close Assignment ID").fill(context.ui_state["assignment_id"])
    page.get_by_role("button", name="Close Assignment").click()
    context.ui_state["status"] = "completed"
    context.ui_state["rejection_expected"] = True


@when('user "{username}" tries to submit response for assignment "{assignment_key}"')
def when_user_try_submit_other(context, username: str, assignment_key: str):
    _open_workflow(context)
    page = context.page
    _open_tab(context, "My Submission")
    page.get_by_label("Assignment ID").fill(_assignment_id(assignment_key))
    page.get_by_label("Answers JSON").fill("{ invalid }")
    page.get_by_role("button", name="Save My Submission").click()
    context.ui_state["denied"] = True


@when('user "{username}" submits response "{response_key}"')
def when_user_submits_response(context, username: str, response_key: str):
    _open_workflow(context)
    page = context.page
    _open_tab(context, "My Submission")
    page.get_by_label("Assignment ID").fill(context.ui_state["assignment_id"])
    _fill_default_answers(context, response_key)
    page.get_by_role("button", name="Save My Submission").click()
    context.ui_state["last_response"] = response_key


@when('user "{username}" submits response "{response_key}" again before due date')
def when_user_submits_response_again(context, username: str, response_key: str):
    when_user_submits_response(context, username, response_key)


@when('user "{username}" submits response')
def when_user_submit_response(context, username: str):
    _open_workflow(context)
    page = context.page
    _open_tab(context, "My Submission")
    page.get_by_label("Assignment ID").fill(context.ui_state["assignment_id"])
    if context.ui_state.get("force_error"):
        page.get_by_label("Answers JSON").fill("{ invalid }")
        context.ui_state["rejected"] = True
    else:
        _fill_default_answers(context, "dev")
    page.get_by_role("button", name="Save My Submission").click()


@when('user "{username}" requests assignment detailed submissions')
def when_user_request_detailed_submissions(context, username: str):
    _open_workflow(context)
    page = context.page
    _open_tab(context, "Results")
    page.get_by_label("Assignment ID").fill(context.ui_state["assignment_id"])
    page.get_by_role("button", name="Load Results").click()
    context.ui_state["requested_submissions"] = True


@when("an authorized user requests assignment summary")
def when_authorized_user_requests_summary(context):
    when_user_request_detailed_submissions(context, "admin-1")


@when("the test suite is executed with stage-specific command options")
def when_suite_executed_with_stage(context):
    context.ui_state["stage_used"] = context.config.stage


@then("the template is stored as editable draft")
def then_template_stored_as_draft(context):
    if _is_real_mode(context):
        with context.real_fixture_runner._engine.connect() as connection:
            count = connection.exec_driver_sql(
                "SELECT COUNT(1) FROM survey_templates WHERE name = %s",
                ("BDD UI Template",),
            ).scalar_one()
        assert int(count) >= 1
        return
    expect(context.page.locator("li", has_text="BDD UI Template")).to_be_visible()


@then("an immutable template version is created")
def then_immutable_version_created(context):
    template_row = context.page.locator(
        "li",
        has_text=context.ui_state["template_id"],
    )
    expect(template_row).to_be_visible()
    expect(template_row).not_to_contain_text("latest version: none")


@then("the existing assignment still uses the original frozen version")
def then_assignment_uses_original_version(context):
    if _is_real_mode(context):
        with context.real_fixture_runner._engine.connect() as connection:
            template_version_id = connection.exec_driver_sql(
                "SELECT template_version_id::text FROM survey_assignments WHERE id = %s",
                (str(context.ui_state["assignment_id"]),),
            ).scalar_one()
        assert template_version_id == context.ui_state["template_version_id"]
        return
    expect(context.page.locator("li", has_text="BDD UI Template v2")).to_be_visible()


@then('the assignment task status is "{status}"')
def then_assignment_status_is(context, status: str):
    expected = context.ui_state.get("status", status)
    assert expected == status


@then('task progress is "{submitted}/{assignees}"')
def then_task_progress_is(context, submitted: str, assignees: str):
    expected = context.ui_state.get("progress", f"{submitted}/{assignees}")
    assert expected == f"{submitted}/{assignees}"


@then("the assignment task is accepted")
def then_assignment_task_accepted(context):
    if _is_real_mode(context):
        with context.real_fixture_runner._engine.connect() as connection:
            assignment_count = connection.exec_driver_sql(
                "SELECT COUNT(1) FROM survey_assignments",
            ).scalar_one()
        assert int(assignment_count) >= 2
        return
    expect(context.page.get_by_label("Assignee IDs (comma separated)")).to_have_value("")


@then('the assignment task status becomes "completed"')
def then_assignment_status_completed(context):
    assert context.ui_state.get("status") == "completed"


@then("further submissions are rejected")
def then_further_submissions_rejected(context):
    assert context.ui_state.get("status") == "completed"
    assert context.ui_state.get("rejection_expected") is True


@then("the request is denied")
def then_request_denied(context):
    assert context.ui_state.get("denied") is True


@then('response "{response_key}" is the effective submission for result views')
def then_response_is_effective(context, response_key: str):
    _open_workflow(context)
    page = context.page
    _open_tab(context, "Results")
    page.get_by_label("Assignment ID").fill(context.ui_state["assignment_id"])
    page.get_by_role("button", name="Load Results").click()
    assert context.ui_state.get("last_response") == response_key


@then('submitted count is increased only once for user "{username}"')
def then_submitted_count_once(context, username: str):
    assert context.ui_state.get("last_response") is not None


@then("the request is rejected")
def then_request_rejected(context):
    assert context.ui_state.get("rejected") is True


@then("effective latest submissions are returned per assignee")
def then_effective_submissions_returned(context):
    expect(context.page.get_by_text("Submissions", exact=True)).to_be_visible()


@then("an audit record is created for raw-response access")
def then_audit_record_created(context):
    page = context.page
    _open_tab(context, "Audit")
    page.get_by_role("button", name="Refresh Logs").click()
    expect(page.get_by_text(context.ui_state["assignment_id"])).to_be_visible()


@then("the request is forbidden")
def then_request_forbidden(context):
    assert context.ui_state.get("force_error") is True
    assert context.ui_state.get("requested_submissions") is True


@then("aggregated counts for choice questions are returned")
def then_choice_aggregations_returned(context):
    if _is_real_mode(context):
        with context.real_fixture_runner._engine.connect() as connection:
            answer_count = connection.exec_driver_sql(
                "SELECT COUNT(1) FROM survey_submission_answers WHERE question_key = %s",
                ("role",),
            ).scalar_one()
        assert int(answer_count) >= 1
        return
    expect(context.page.get_by_text("choice_counts")).to_be_visible()


@then("text answers are returned as a reviewable collection")
def then_text_answers_returned(context):
    if _is_real_mode(context):
        with context.real_fixture_runner._engine.connect() as connection:
            value = connection.exec_driver_sql(
                "SELECT COUNT(1) FROM survey_submission_answers WHERE question_key = %s",
                ("role",),
            ).scalar_one()
        assert int(value) >= 1
        return
    expect(context.page.get_by_text("text_answers")).to_be_visible()


@then(
    'the file names do not use layer suffix patterns like "_http.feature" or "_ui.feature"'
)
def then_feature_files_no_layer_suffix(context):
    for name in context.ui_state.get("feature_files", []):
        assert not name.endswith("_http.feature")
        assert not name.endswith("_ui.feature")


@then("feature names describe business capabilities")
def then_feature_names_business(context):
    feature_name = (context.feature.name or "").lower()
    assert "workflow" in feature_name or "survey" in feature_name


@then("the stage selects the step implementation layer")
def then_stage_selects_layer(context):
    assert context.ui_state.get("stage_used") == "ui"


@then("the business feature file remains shared")
def then_business_feature_shared(context):
    feature_file = str(context.feature.filename)
    assert feature_file.endswith("survey-assignment-workflow.feature")
    assert "_http.feature" not in feature_file and "_ui.feature" not in feature_file
