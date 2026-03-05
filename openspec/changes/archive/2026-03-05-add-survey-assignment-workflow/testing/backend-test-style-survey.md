# Backend Test Style Survey (Task 0.3)

This survey summarizes existing backend test conventions to keep new survey-module tests consistent with current repository style.

## Scope Reviewed

- `backend/tests/app/unit/domain/**`
- `backend/tests/app/unit/application/**`
- `backend/tests/app/unit/infrastructure/**`
- `backend/tests/app/integration/**`
- `backend/pyproject.toml` (`tool.pytest.ini_options`, `ruff` pytest rules)

## Observed Conventions

## 1) Naming and structure

- Test file naming: `test_<unit>.py`
- Test function naming: `test_<behavior>()`
- Behavior-first wording is preferred (e.g., `test_creates_active_user_with_hashed_password`)
- Tests are grouped by architectural layer directory:
  - `unit/domain`
  - `unit/application`
  - `unit/infrastructure`
  - `integration/...`

## 2) AAA flow and assertion style

- Most tests use explicit Arrange/Act/Assert blocks for non-trivial cases.
- Assertions use plain `assert`.
- Exception checks use `with pytest.raises(...)`.
- Parametrized tests use `@pytest.mark.parametrize` with clear `id=...`.

## 3) Async and marks

- Async tests use `@pytest.mark.asyncio`.
- Slow hashing tests use `@pytest.mark.slow`.
- Default pytest options skip slow tests (`addopts = "-m 'not slow'"`), so slow tests are opt-in.

## 4) Factories and fixtures

- Reusable data builders under `tests/app/unit/factories/*`.
- Layer-level fixtures in local `conftest.py` files.
- Infrastructure tests often inject fixture-provided constructor partials/mocks.

## 5) Typing and lint expectations

- Type hints are present on test signatures and locals where useful.
- Some targeted ignores are accepted (for mock typing, etc.), but kept minimal.
- Pytest style is linted by Ruff (`PT` rules enabled).

## 6) Integration test posture

- Current integration tests are lightweight and focus on deterministic behavior without external runtime dependencies.
- For new survey integration tests, keep DB interaction explicit and bounded to scenario-specific setup.

## Layer-specific guidance for new survey module

- Domain tests:
  - validate invariants, transitions, and immutable-version semantics.
- Application tests:
  - verify command/query orchestration and permission decisions.
- Infrastructure tests:
  - verify repository persistence and gateway contracts.
- Integration tests:
  - validate end-to-end persistence behavior and aggregation correctness.

## Mandatory consistency constraints

1. Follow existing naming and directory layout.
2. Use AAA style for readability in all non-trivial tests.
3. Prefer factory helpers over ad-hoc inline test data duplication.
4. Keep async/slow markers consistent with existing patterns.
5. Keep mock boundaries at layer boundaries, not across unrelated layers.
