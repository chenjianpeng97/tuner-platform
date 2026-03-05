# Frontend i18n key convention

This module uses two namespaces:

- `common.*`: shared UI and shell components (search, theme, profile, navigation labels).
- `business.*`: business-domain pages and flows (surveys, users, account).

## Naming rules

- Use hierarchical keys: `<namespace>.<module>.<section>.<name>`.
- Keep labels and actions separate, for example:
  - `common.profile.signOut`
  - `business.users.actions.edit`
- Keep status and column labels grouped under page modules, for example:
  - `business.surveys.templates.status.draft`
  - `business.surveys.templates.columns.name`

## Locale files

- `src/i18n/resources/en/common.ts`
- `src/i18n/resources/en/business.ts`
- `src/i18n/resources/zh/common.ts`
- `src/i18n/resources/zh/business.ts`
