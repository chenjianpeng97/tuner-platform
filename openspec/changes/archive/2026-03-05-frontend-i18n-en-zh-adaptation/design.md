## Context

The frontend currently renders user-visible copy mostly as static strings, with no unified locale layer. This change introduces cross-cutting i18n behavior (app bootstrap, shared components, and business pages), so decisions must be aligned before implementation. Constraints include keeping default language as English, supporting Chinese switching in runtime, and minimizing disruption to existing route/component structure.

## Goals / Non-Goals

**Goals:**
- Provide a single i18n runtime foundation in frontend app initialization with `en` default and `zh` alternative.
- Support deterministic language switching and persistence across page refreshes.
- Standardize translation key organization for common components and business pages to avoid ad-hoc string handling.
- Define fallback behavior when translation keys are missing, prioritizing resilient UI rendering.

**Non-Goals:**
- Introducing additional locales beyond `en` and `zh` in this change.
- Rewriting all frontend modules at once outside common components and business-scoped pages.
- Backend localization or API-level language negotiation.
- Content quality review for every translated sentence (handled by product/content workflow).

## Decisions

1. Adopt a dedicated frontend i18n runtime and mount it at app bootstrap.
   - Rationale: central initialization guarantees all downstream components/routes can consume locale state consistently.
   - Alternative considered: per-page i18n setup. Rejected due to duplicated setup and inconsistent fallback logic.

2. Use locale resource files segmented by functional domain (`common`, `business`) and locale (`en`, `zh`).
   - Rationale: aligns with requested scope and keeps translation ownership clear.
   - Alternative considered: one flat locale file per language. Rejected due to poor maintainability and merge conflicts as scale grows.

3. Persist selected locale in browser storage with startup precedence: stored locale → default `en`.
   - Rationale: predictable user experience while preserving explicit user selection.
   - Alternative considered: always reset to default on reload. Rejected because it breaks user expectation after switching.

4. Establish key naming convention using hierarchical namespaces (e.g., `common.button.submit`, `business.user.list.title`).
   - Rationale: enables discoverability and prevents key collisions.
   - Alternative considered: short unscoped keys. Rejected due to collision risk and weak traceability.

5. Define missing-key behavior as: render fallback from default locale first; if absent, render key string and log warning in development.
   - Rationale: UI remains usable while making gaps visible during development/testing.
   - Alternative considered: hard failure on missing key. Rejected due to high risk of blocking UI in partial migration.

## Risks / Trade-offs

- [Risk] Partial migration leaves mixed hardcoded and localized text in business pages → Mitigation: define migration checklist per page and gate completion via UI verification in both locales.
- [Risk] Key naming drift across teams causes inconsistent lookup paths → Mitigation: document namespace rules and enforce via review checklist/lint conventions where possible.
- [Risk] Locale persistence value becomes invalid after future refactors → Mitigation: validate stored locale against supported set at startup and fallback to `en`.
- [Risk] Translation files grow and impact bundle size → Mitigation: keep domain-based resource split and evaluate lazy-loading strategy in a follow-up if needed.

## Migration Plan

1. Introduce i18n runtime bootstrap with `en` default and `zh` support.
2. Add locale switch UI/control integration at shared app level.
3. Migrate common/shared components to translation keys.
4. Migrate business pages under agreed scope using namespaced keys.
5. Validate UI rendering for `en` and `zh`, including fallback and persistence behavior.
6. Rollback strategy: disable locale switch entry and revert to default `en` resources while keeping non-breaking runtime initialization if needed.

## Open Questions

- Should locale switcher placement be global header-only or also available in selected business pages?
- Is server-side user preference sync required now, or deferred to a later change?
- Do we want strict CI checks for missing keys in this change, or post-change hardening?