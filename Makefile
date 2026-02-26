SHELL := /bin/bash
APP_ENV ?= local

.PHONY: bdd-http frontend-dev backend-dev backend-dev-doc dev

bdd-http:
	uv run --group bdd behave --stage http --tags http

frontend-dev:
	pnpm --dir frontend run dev

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
