SHELL := /bin/bash
APP_ENV ?= local

.PHONY: bdd-http frontend-dev backend-dev dev

bdd-http:
	uv run --group bdd behave --stage http --tags http

frontend-dev:
	pnpm --dir frontend run dev

backend-dev:
	APP_ENV=$(APP_ENV) uv run --project backend python -m app.run

dev:
	$(MAKE) -j2 backend-dev frontend-dev
