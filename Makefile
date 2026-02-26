.PHONY: bdd-http

bdd-http:
	uv run --group bdd behave --stage http --tags http
