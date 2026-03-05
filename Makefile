SHELL := /bin/bash
APP_ENV ?= local

.PHONY: bdd-http bdd-http-mock bdd-http-real bdd-ui bdd-ui-mock bdd-ui-dev frontend-dev frontend-dev-mock frontend-api-generate frontend-api-typecheck frontend-mock-init backend-dev backend-dev-doc dev

bdd-http:
	BDD_HTTP_MODE=mock uv run --group bdd behave --stage http --tags http

bdd-http-mock:
	BDD_HTTP_MODE=mock uv run --group bdd behave --stage http --tags http

bdd-http-real:
	BDD_HTTP_MODE=real uv run --group bdd behave --stage http --tags http

bdd-ui:
	BDD_UI_MODE=mock uv run --group bdd behave --stage ui features/survey-assignment-workflow.feature

bdd-ui-mock:
	BDD_UI_MODE=mock uv run --group bdd behave --stage ui features/survey-assignment-workflow.feature

bdd-ui-dev:
	BDD_UI_MODE=dev uv run --group bdd behave --stage ui features/survey-assignment-workflow.feature

frontend-dev:
	pnpm --dir frontend run dev

frontend-dev-mock:
	pnpm --dir frontend run dev:mock

frontend-api-generate:
	pnpm --dir frontend run api:generate

frontend-api-typecheck:
	pnpm --dir frontend exec tsc -p tsconfig.app.json --noEmit

frontend-mock-init:
	pnpm --dir frontend run mock:init

backend-dev:
	APP_ENV=$(APP_ENV) uv run --project backend python -m app.run

backend-dev-doc:
	@set -e; \
	APP_ENV=$(APP_ENV) uv run --project backend python -m app.run & \
	pid=$$!; \
	trap 'kill $$pid' INT TERM EXIT; \
	until curl -fsS http://127.0.0.1:8000/openapi.json >/dev/null; do sleep 1; done; \
	curl -fsS http://127.0.0.1:8000/openapi.json -o docs/api_doc.json; \
	echo "Exported API doc to docs/api_doc.json"; \
	wait $$pid

dev:
	$(MAKE) -j2 backend-dev frontend-dev
