## Context

HTTP-stage BDD tests currently validate orchestration by injecting mocked presentation-layer interface services, while UI-stage tests already support runtime mode switching (`mock` and `dev`). The missing piece is a unified HTTP-stage execution model that can run the same scenarios in two modes: fast orchestration validation with mocks and DB-backed integration validation with real backend services.

This change touches multiple modules (`features/` test bootstrap, step wiring, backend fixture/bootstrap, and command entrypoints), so a shared design is required to prevent duplicated steps and diverging scenario contracts.

## Goals / Non-Goals

**Goals:**
- Add a single HTTP-stage mode selector (`mock` | `real`) that controls dependency binding without changing feature files.
- Reuse the same Gherkin scenarios and step definitions across modes.
- Keep mock mode deterministic and fast for orchestration checks.
- Enable real mode to validate integration behavior against real adapters and DB state.
- Align mode naming and invocation semantics with existing UI-stage conventions where practical.

**Non-Goals:**
- Rewriting existing business scenarios or introducing a second feature suite for real mode.
- Changing production runtime DI behavior; this is limited to test-stage bootstrap/wiring.
- Replacing existing UI-stage execution strategy.

## Decisions

1. **Introduce explicit HTTP-stage binding mode in environment bootstrap**
   - Decision: Add a single mode source (env var/cli passthrough) resolved early in HTTP test environment setup.
   - Rationale: Prevent per-step branching and keep mode decision centralized.
   - Alternative considered: In-step conditional service selection. Rejected due to high maintenance and behavior drift risk.

2. **Use DI-container composition to swap adapters, not scenario logic**
   - Decision: Keep step definitions unchanged; swap container providers for `mock` vs `real` at setup time.
   - Rationale: Preserves contract-level scenario reuse and avoids duplicate step files.
   - Alternative considered: Duplicate HTTP stage into `http-mock` and `http-real`. Rejected because of duplicated scenarios and higher divergence risk.

3. **Define separate test prerequisites for each mode**
   - Decision: Mock mode uses isolated fakes/stubs; real mode requires DB/bootstrap readiness and real service wiring.
   - Rationale: Makes failure domains explicit and improves CI diagnostics.
   - Alternative considered: Auto-fallback from real to mock when DB unavailable. Rejected to avoid false green integration signals.

4. **Standardize command-level invocation for local and CI**
   - Decision: Expose mode via make/pnpm-compatible command conventions and document matrix execution.
   - Rationale: Keeps operator workflow consistent across HTTP/UI acceptance layers.
   - Alternative considered: Hidden internal toggle only. Rejected due to poor discoverability and weak CI control.

5. **Adopt shared real-mode fixture scripts for DB reset + seed + auth bootstrap**
   - Decision: Introduce one shared fixture toolchain for real mode, callable by both HTTP-stage and UI-stage hooks, with per-scenario lifecycle: `cleanup -> seed -> auth bootstrap`.
   - Rationale: Ensures deterministic test state and avoids duplicated fixture logic between HTTP/UI stacks.
   - Alternative considered: Separate per-stage seed scripts. Rejected due to divergence risk and duplicated maintenance.

6. **Use profile-based seed datasets with stable identities**
   - Decision: Define reusable fixture profiles (e.g., `minimal`, `survey-assignment-baseline`) with stable usernames/IDs to support scenario contracts.
   - Rationale: Reduces scenario flakiness and enables direct reuse of business feature files in real mode.
   - Alternative considered: Ad-hoc per-step DB writes. Rejected because it scatters data setup and couples steps to storage details.

7. **Standardize real-mode authentication bootstrap for both stages**
   - Decision: Seed canonical test users and create authenticated session context in fixture bootstrap; HTTP uses session cookie injection in TestClient, UI uses browser cookie/session bootstrap via the same seeded identities.
   - Rationale: Removes per-step auth hacks and aligns authorization behavior with real backend runtime.
   - Alternative considered: Anonymous flow + bypassed auth checks in real mode. Rejected because it invalidates integration acceptance semantics.

## Risks / Trade-offs

- [Real mode flakiness from shared DB state] → Add per-scenario setup/teardown contracts and deterministic fixture seeding.
- [Longer pipeline duration when running both modes] → Keep mock mode as default quick gate; run real mode in integration-quality gate or selective matrix.
- [Mode drift due to adapter behavior differences] → Enforce identical scenario set and add explicit assertions for response contract parity.
- [Bootstrap complexity increase] → Centralize mode resolution and DI assembly in one environment module with minimal branching.
- [Shared fixture scripts become slow for every scenario] → Keep cleanup/seed idempotent and profile-scoped; optimize heavy datasets via minimal baseline profiles.
- [Auth bootstrap drifts between HTTP and UI] → Use one shared bootstrap contract and expose stage-specific adapters only for cookie/session transport.

## Migration Plan

1. Add HTTP-stage mode configuration entrypoint and default to `mock` for backward compatibility.
2. Refactor HTTP environment wiring to build container by mode (`mock` or `real`) while preserving current step APIs.
3. Introduce shared real-mode fixture scripts (`cleanup`, `seed`, `auth-bootstrap`) and call them from both HTTP/UI real-mode hooks.
4. Add/adjust make targets and CI job parameters for mode-specific and matrix execution.
5. Roll out with parallel verification (run current mock path + new explicit mock mode), then enable real mode gate with shared per-scenario fixtures.

Rollback: switch mode default and CI invocation back to mock-only path; keep feature/step files unchanged.

## Open Questions

- Should real mode run on every PR or only on protected branches/nightly quality gates?
- Should real-mode fixture profile selection be driven by feature tags, scenario tags, or a single global baseline profile?
- Do we require strict output parity between mock and real for all scenarios, or allow documented exceptions for integration-only fields?