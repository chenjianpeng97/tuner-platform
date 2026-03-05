## ADDED Requirements

### Requirement: Common UI components SHALL consume translation keys
Shared/common UI components in frontend SHALL render user-facing copy via locale keys and locale resources, not hardcoded literal strings.

#### Scenario: Common component renders localized label
- **WHEN** a common component is rendered under locale `zh`
- **THEN** its user-facing labels are resolved from Chinese locale resources
- **THEN** switching back to `en` renders the English labels for the same keys

### Requirement: Business pages SHALL support bilingual rendering
Pages under the business scope SHALL provide English and Chinese translations for user-facing text within the page shell and primary interaction content.

#### Scenario: Business page text changes with locale switch
- **WHEN** user opens a business page and changes locale from `en` to `zh`
- **THEN** page title, action labels, and table/form prompts update to Chinese translations
- **THEN** switching back to `en` restores English translations for the same keys

### Requirement: Locale resources SHALL be organized by domain and locale
Frontend translation resources SHALL be organized to separate `common` and `business` domains for each supported locale (`en`, `zh`).

#### Scenario: Resource lookup resolves by domain namespace
- **WHEN** a business page requests key `business.*`
- **THEN** the key is resolved from business-domain resources for the active locale
- **THEN** a common component key `common.*` is resolved from common-domain resources

### Requirement: Missing translation keys SHALL use resilient fallback behavior
If a translation key is missing in the active locale, frontend SHALL fallback to English for that key; if the key is also missing in English, frontend SHALL render a stable key placeholder string.

#### Scenario: Missing Chinese key falls back to English key value
- **WHEN** active locale is `zh` and key exists only in English resources
- **THEN** frontend displays the English value for that key
- **THEN** page remains functional without crashing or blank text containers