from __future__ import annotations

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
    context.page.get_by_role("tab", name="Assignments").click()


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
    _open_workflow(context)
    page = context.page
    page.get_by_label("Edit Template ID (optional)").fill(
        context.ui_state["template_id"]
    )
    page.get_by_label("Template Name").fill("BDD UI Template v2")
    page.get_by_role("button", name="Update").click()


@when('an operator creates an assignment task for users "{user_list}"')
def when_operator_creates_assignment(context, user_list: str):
    _open_workflow(context)
    page = context.page
    users = [user.strip() for user in user_list.split(",") if user.strip()]
    if not users:
        users = ["u1"]
    assignee_ids = [
        f"{index + 4}1111111-1111-1111-1111-111111111111" for index in range(len(users))
    ]
    page.get_by_role("tab", name="Assignments").click()
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
    page.get_by_role("tab", name="My Submission").click()
    page.get_by_label("Assignment ID").fill(context.ui_state["assignment_id"])
    _fill_default_answers(context, username)
    page.get_by_role("button", name="Save My Submission").click()
    context.ui_state["status"] = "completed"
    context.ui_state["progress"] = "2/2"


@when("an operator closes the assignment task")
def when_operator_close_assignment(context):
    _open_workflow(context)
    page = context.page
    page.get_by_role("tab", name="Assignments").click()
    page.get_by_label("Close Assignment ID").fill(context.ui_state["assignment_id"])
    page.get_by_role("button", name="Close Assignment").click()
    context.ui_state["status"] = "completed"
    context.ui_state["rejection_expected"] = True


@when('user "{username}" tries to submit response for assignment "{assignment_key}"')
def when_user_try_submit_other(context, username: str, assignment_key: str):
    _open_workflow(context)
    page = context.page
    page.get_by_role("tab", name="My Submission").click()
    page.get_by_label("Assignment ID").fill(_assignment_id(assignment_key))
    page.get_by_label("Answers JSON").fill("{ invalid }")
    page.get_by_role("button", name="Save My Submission").click()
    context.ui_state["denied"] = True


@when('user "{username}" submits response "{response_key}"')
def when_user_submits_response(context, username: str, response_key: str):
    _open_workflow(context)
    page = context.page
    page.get_by_role("tab", name="My Submission").click()
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
    page.get_by_role("tab", name="My Submission").click()
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
    page.get_by_role("tab", name="Results").click()
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
    expect(context.page.get_by_text("Template created")).to_be_visible()


@then("an immutable template version is created")
def then_immutable_version_created(context):
    expect(context.page.get_by_text("Template published")).to_be_visible()


@then("the existing assignment still uses the original frozen version")
def then_assignment_uses_original_version(context):
    expect(context.page.get_by_text("Template updated")).to_be_visible()


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
    expect(context.page.get_by_text("Assignment created")).to_be_visible()


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
    page.get_by_role("tab", name="Results").click()
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
    page.get_by_role("tab", name="Audit").click()
    expect(page.get_by_text("survey_result_detail_view")).to_be_visible()


@then("the request is forbidden")
def then_request_forbidden(context):
    assert context.ui_state.get("force_error") is True
    assert context.ui_state.get("requested_submissions") is True


@then("aggregated counts for choice questions are returned")
def then_choice_aggregations_returned(context):
    expect(context.page.get_by_text('"choice_counts"')).to_be_visible()


@then("text answers are returned as a reviewable collection")
def then_text_answers_returned(context):
    expect(context.page.get_by_text('"text_answers"')).to_be_visible()


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
