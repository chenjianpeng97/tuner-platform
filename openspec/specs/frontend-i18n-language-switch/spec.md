# frontend-i18n-language-switch Specification

## Purpose
Define required frontend behavior for English/Chinese locale initialization, runtime switching, persistence, and locale fallback.

## Requirements
### Requirement: Frontend SHALL default to English locale
The frontend application SHALL initialize locale as `en` when no valid persisted user locale is available.

#### Scenario: First-time visitor sees English by default
- **WHEN** user opens the frontend with no persisted locale
- **THEN** the active locale is `en`
- **THEN** user-visible translated text renders from English resources

### Requirement: Frontend SHALL support runtime switching between English and Chinese
The frontend SHALL provide a language switch capability that allows users to change locale between `en` and `zh` during runtime.

#### Scenario: User switches locale from English to Chinese
- **WHEN** user triggers language switch from `en` to `zh`
- **THEN** active locale changes to `zh`
- **THEN** translated UI text updates to Chinese without requiring user logout

### Requirement: Frontend SHALL persist user-selected locale
The frontend SHALL persist the user's selected locale and restore it on subsequent visits when the persisted value is supported.

#### Scenario: Persisted Chinese locale is restored
- **WHEN** user previously selected `zh` and reopens the frontend
- **THEN** active locale is restored to `zh`
- **THEN** Chinese translations render on initial page load

### Requirement: Frontend SHALL apply deterministic fallback for invalid or missing locale data
The frontend SHALL validate locale resolution and fallback to `en` for unsupported persisted locale values.

#### Scenario: Unsupported persisted locale falls back to English
- **WHEN** persisted locale value is not one of `en` or `zh`
- **THEN** active locale falls back to `en`
- **THEN** UI remains renderable using English resources
