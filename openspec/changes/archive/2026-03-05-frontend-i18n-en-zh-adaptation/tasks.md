## 1. i18n Runtime Foundation

- [x] 1.1 Select and configure frontend i18n runtime in app bootstrap with supported locales `en` and `zh`
- [x] 1.2 Implement locale resolution precedence (persisted locale if valid, otherwise default `en`)
- [x] 1.3 Implement locale persistence update flow when user changes language
- [x] 1.4 Implement invalid persisted locale guard that falls back to `en`

## 2. Locale Resources and Conventions

- [x] 2.1 Create locale resource structure by domain and locale (common/business × en/zh)
- [x] 2.2 Define and document key namespace convention for `common.*` and `business.*`
- [x] 2.3 Add initial English and Chinese translation entries required by current common/business scope
- [x] 2.4 Implement missing-key fallback behavior (active locale → `en` → stable key placeholder)

## 3. Language Switch UX Integration

- [x] 3.1 Add language switch UI entry in shared app shell
- [x] 3.2 Wire switch action to runtime locale update and resource re-rendering
- [x] 3.3 Verify locale switch works without logout and reflects immediately across visible UI

## 4. Common Components and Business Pages Adaptation

- [x] 4.1 Inventory target common components and replace hardcoded user-facing strings with translation keys
- [x] 4.2 Inventory target business pages and replace page-level hardcoded strings with translation keys
- [x] 4.3 Ensure business page titles, actions, and table/form prompts are localized in both locales
- [x] 4.4 Remove or flag any remaining hardcoded bilingual-scope strings in touched modules

## 5. Verification and Delivery

- [x] 5.1 Validate first-load default locale is English for users without persisted preference
- [x] 5.2 Validate persisted locale restore behavior across refresh and revisit
- [x] 5.3 Validate bilingual rendering for adapted common components under `en` and `zh`
- [x] 5.4 Validate bilingual rendering for adapted business pages under `en` and `zh`
- [x] 5.5 Run frontend checks/tests and update change notes with verification evidence

## Verification Evidence

- `pnpm exec eslint` executed on all changed i18n-related files (0 errors, TanStack React Compiler compatibility warnings only).
- `pnpm run build` succeeded (`tsc -b` + `vite build`) after integration fixes.