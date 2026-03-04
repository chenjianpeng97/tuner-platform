@http
Feature: Survey assignment workflow
  The system manages survey templates, assignment tasks, assignee submissions,
  progress tracking, and result visibility.
  This feature is business-oriented and stage-agnostic.
  HTTP/UI step implementations MUST be selected by "--stage", not by splitting
  this feature into layer-specific files.

  Rule: Template authoring and version freezing
    Scenario: Create template with supported question types
      Given an authorized survey operator
      When the operator creates a survey template with single choice, multi choice, and text questions
      Then the template is stored as editable draft

    Scenario: Publish template creates immutable version
      Given an editable survey template exists
      When the operator publishes the template
      Then an immutable template version is created

    Scenario: Assignment uses frozen version after template edit
      Given a published template version is used by an assignment task
      When the operator updates the editable template content later
      Then the existing assignment still uses the original frozen version

  Rule: Assignment task lifecycle and progress
    Scenario: Create assignment task for specific users
      Given an immutable template version exists
      When an operator creates an assignment task for users "u1,u2,u3"
      Then the assignment task status is "in_progress"
      And task progress is "0/3"

    Scenario: Assignment supports optional due date
      Given an immutable template version exists
      When an operator creates an assignment task without due date
      Then the assignment task is accepted

    Scenario: Assignment progress shows partial milestone 10/12
      Given an in-progress assignment task for users "u1,u2,u3"
      And task progress is "10/12"
      Then task progress is "10/12"

    Scenario: Assignment progress shows completion milestone 12/12
      Given an in-progress assignment task for users "u1,u2,u3"
      And task progress is "12/12"
      Then the assignment task status becomes "completed"
      And task progress is "12/12"

    Scenario: Assignment auto-completes when all assignees submitted
      Given an in-progress assignment task for users "u1,u2"
      And user "u1" has submitted
      When user "u2" submits successfully
      Then the assignment task status becomes "completed"
      And task progress is "2/2"

    Scenario: Operator can close assignment early
      Given an in-progress assignment task for users "u1,u2,u3"
      And task progress is "1/3"
      When an operator closes the assignment task
      Then the assignment task status becomes "completed"
      And further submissions are rejected

  Rule: Assignee submission behavior
    Scenario: Only assignee can submit own response
      Given assignment task "A-1" is assigned to user "u1"
      When user "u2" tries to submit response for assignment "A-1"
      Then the request is denied

    Scenario: Latest submission wins before close or due date
      Given assignment task "A-1" is in progress and assigned to user "u1"
      When user "u1" submits response "R1"
      And user "u1" submits response "R2" again before due date
      Then response "R2" is the effective submission for result views
      And submitted count is increased only once for user "u1"

    Scenario: Submissions are blocked after due date
      Given assignment task "A-1" has due date in the past
      When user "u1" submits response
      Then the request is rejected

  Rule: Result visibility and auditing
    Scenario: Authorized user views detailed submissions
      Given assignment task "A-1" has at least one effective submission
      And user "admin-1" has survey-library permission
      When user "admin-1" requests assignment detailed submissions
      Then effective latest submissions are returned per assignee
      And an audit record is created for raw-response access

    Scenario: Unauthorized user cannot view detailed submissions
      Given assignment task "A-1" has at least one effective submission
      And user "viewer-1" does not have survey-library permission
      When user "viewer-1" requests assignment detailed submissions
      Then the request is forbidden

    Scenario: Summary endpoint returns aggregation
      Given assignment task "A-1" has multiple submissions
      When an authorized user requests assignment summary
      Then aggregated counts for choice questions are returned
      And text answers are returned as a reviewable collection

  Rule: Quality gate and test-organization constraints
    Scenario: Feature naming is business-oriented
      Given a team adds new acceptance feature files for survey workflow
      Then the file names do not use layer suffix patterns like "_http.feature" or "_ui.feature"
      And feature names describe business capabilities

    Scenario: Stage controls step implementation
      Given the same survey assignment feature must be validated at HTTP and UI layers
      When the test suite is executed with stage-specific command options
      Then the stage selects the step implementation layer
      And the business feature file remains shared
