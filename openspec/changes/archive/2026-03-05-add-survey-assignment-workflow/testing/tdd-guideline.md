# Survey Workflow TDD Guideline (Task 0.4)

This guideline defines how survey-assignment implementation must follow Red-Green-Refactor while aligning with current backend test style.

## Red-Green-Refactor policy

For each implementation slice:

1. **Red**
  - Add a failing test that expresses expected behavior from OpenSpec requirement/scenario.
  - Ensure failure reason is relevant (not setup/import failure).
2. **Green**
  - Add minimal production code to satisfy the failing test.
  - Avoid speculative implementation beyond current test behavior.
3. **Refactor**
  - Improve code readability/structure without behavior change.
  - Keep tests green after each refactor step.

## Slice strategy

Use small vertical slices:

- Domain rule first (entity/value object/service behavior)
- Application orchestration next (command/query + permission policy)
- HTTP controller contract next (request/response/error-map)
- Persistence and aggregation next

Do not implement entire module before having corresponding tests.

## Mapping rule: requirement -> tests

Each OpenSpec requirement must map to at least one test at one or more layers:

- Domain invariant: domain unit test
- Orchestration/authorization: application unit test
- HTTP contract: HTTP-stage behave scenario
- Persistence aggregation: integration test

## Fixture and mock boundaries

- Domain tests:
  - use factories from `tests/app/unit/factories`.
  - avoid DB/network mocks.
- Application tests:
  - mock only ports/gateways injected by use case.
- Infrastructure tests:
  - validate concrete adapter behavior with bounded setup.
- HTTP-stage behave:
  - mock interactors/handlers (controller-level isolation).

## Coverage target policy

Change-level coverage should prioritize behavior risk:

- Must cover all acceptance-critical scenarios:
  - version freeze
  - progress counting (`10/12`, `12/12`)
  - latest submission wins
  - due-time blocking
  - permission denial
  - manual close completion
- New code should not reduce existing coverage baselines for touched modules.

## Naming and organization constraints

- Keep test names behavior-oriented: `test_<expected_behavior>`.
- Keep business acceptance feature files layer-agnostic.
- Do not create layer-suffixed feature files such as `*_http.feature` or `*_ui.feature`.
- Use stage selection (`behave --stage`) to bind layer-specific step implementations.

## Quality gate before merge

A survey slice is merge-ready only if:

1. Unit/integration tests for the slice are green.
2. HTTP-stage Behave scenarios for the slice are green.
3. No feature-file organization rule is violated.
4. UI-stage Behave scenarios for impacted flow are green (when UI slice is included).
