## Why

Current BDD acceptance testing is split between HTTP-stage orchestration tests (mocked presentation services) and UI-stage validation (mock/e2e via frontend server mode), but HTTP-stage cannot switch to real backend services for integrated DB-backed acceptance. This limits confidence in end-to-end behavior and forces separate test paths for orchestration vs integration.

## What Changes

- Introduce a configurable HTTP-stage execution mode to run the same BDD scenarios against either mocked interface services or real backend API services.
- Standardize dependency wiring so HTTP-stage can choose mock or real adapters at runtime without duplicating feature files.
- Define environment/config conventions for selecting mode in local and CI runs.
- Keep existing UI-stage mode switching (`mock` vs `dev`) and align naming/selection semantics with HTTP-stage for consistency.
- Add acceptance criteria for DB-integrated HTTP-stage runs (real service path) while preserving fast mock-only orchestration checks.

## Capabilities

### New Capabilities
- `bdd-http-service-binding-mode`: Allow HTTP-stage BDD suites to select service binding mode (`mock` or `real`) and execute identical scenario contracts across both.

### Modified Capabilities
- `engineering-quality-gates`: Expand quality-gate requirements to include dual-mode HTTP-stage acceptance coverage and mode-specific execution controls.

## Impact

- Affected areas: BDD environment bootstrap under `features/`, HTTP step wiring, backend test bootstrap/config in `backend/tests` or equivalent integration fixtures, and Makefile/test commands used by local and CI flows.
- Test operations: introduce mode flags/env vars and update docs for running orchestration-only vs DB-integrated acceptance.
- Reliability/performance: preserve fast feedback through mock mode while enabling higher-confidence integrated verification in real mode.