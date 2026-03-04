# Gherkin Baseline Freeze (Task 0.2)

## Scope

Frozen business feature file:

- `features/survey-assignment-workflow.feature`

Coverage includes:

- Template authoring and version freezing
- Assignment task lifecycle and progress
- Assignee submission behavior (including resubmission latest-wins)
- Result visibility, authorization, and auditing
- Quality-gate constraints for feature organization and stage usage

## Review Result

Review outcome: **approved for implementation entry**

Acceptance criteria for "approved":

- Scenarios map to OpenSpec requirements in:
  - `survey-template-management`
  - `survey-assignment-management`
  - `survey-submission-management`
  - `survey-progress-results-visibility`
  - `engineering-quality-gates`
- Feature is business-oriented, not layer-oriented.
- No `_http.feature` / `_ui.feature` naming split is used.
- Stage distinction is explicitly delegated to runner option (`behave --stage`).

## Enforcement Rule

Before business coding for this change:

1. Feature file exists and is review-approved.
2. Any requirement change must first update this baseline (or add compatible business scenarios).
3. Layer-specific step definitions MUST be attached by stage, not by duplicating feature files.
