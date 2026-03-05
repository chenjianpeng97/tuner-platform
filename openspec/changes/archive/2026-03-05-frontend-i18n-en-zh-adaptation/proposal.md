## Why

The frontend currently assumes a single language, which blocks bilingual usability for mixed Chinese/English users and teams. We need a standardized i18n foundation now so upcoming UI work does not duplicate text handling logic or require broad refactors later.

## What Changes

- Add a frontend language framework with English and Chinese locales, with English as the default language.
- Add user-facing language switching between `en` and `zh` in the frontend runtime.
- Adapt shared/common UI components to render locale-based text via i18n resources instead of hardcoded strings.
- Adapt pages under the business domain (`business` scope) to support English/Chinese text display using the same i18n mechanism.
- Define translation resource organization and fallback behavior for missing keys within supported locales.

## Capabilities

### New Capabilities
- `frontend-i18n-language-switch`: Supports runtime English/Chinese switching with default English behavior and locale persistence strategy.
- `frontend-i18n-common-and-business-adaptation`: Defines bilingual adaptation requirements for shared components and business pages.

### Modified Capabilities
- None.

## Impact

- Affected code: frontend app bootstrap, shared UI components, business feature pages, and text resource loading paths in `frontend/src/`.
- Affected dependencies: frontend i18n library/runtime utilities (if not already present in project dependencies).
- Affected QA scope: frontend UI behavior under both `en` and `zh`, including default language, switch behavior, and text coverage in common/business areas.
- No backend API contract changes expected.