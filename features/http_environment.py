"""
Behave HTTP-stage environment (``--stage http``).

Uses FastAPI's ``TestClient`` with a **mocked DI container** so that
**no running server, database, or external service** is required.
Only presentation-layer dependencies are needed:
``fastapi``, ``dishka``, ``fastapi-error-map``, ``httpx``.

The mocked interactors / handlers can be configured per-step via
``context.mocks`` (a :class:`mock_app.MockRegistry` instance).

.. note::

   ``app`` is installed as an **editable workspace package** by
   ``uv sync`` at the monorepo root, so no ``sys.path`` manipulation
   for ``backend/src`` is needed.  Only the ``features/`` directory
   itself is appended so that ``mock_app`` can be imported by name.
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
from typing import Final

# ---------------------------------------------------------------------------
# Ensure ``features/`` is importable so ``mock_app`` resolves by name.
# ``app.*`` is already available via the editable workspace install.
# ---------------------------------------------------------------------------
_FEATURES_DIR = os.path.dirname(os.path.abspath(__file__))
if _FEATURES_DIR not in sys.path:
    sys.path.insert(0, _FEATURES_DIR)

_WORKSPACE_DIR = os.path.dirname(_FEATURES_DIR)
_BACKEND_DIR = os.path.join(_WORKSPACE_DIR, "backend")

from fastapi.testclient import TestClient  # noqa: E402

from mock_app import MockRegistry, create_test_app  # noqa: E402
from real_fixtures import RealFixtureRunner  # noqa: E402
from real_app import create_real_test_app, load_real_settings  # noqa: E402

HTTP_MODE_ENV: Final[str] = "BDD_HTTP_MODE"
HTTP_MODE_DEFAULT: Final[str] = "mock"
HTTP_MODE_ALLOWED: Final[set[str]] = {"mock", "real"}


def _resolve_http_mode() -> str:
    mode = os.getenv(HTTP_MODE_ENV, HTTP_MODE_DEFAULT).strip().lower()
    if mode not in HTTP_MODE_ALLOWED:
        allowed = ", ".join(sorted(HTTP_MODE_ALLOWED))
        raise RuntimeError(
            f"Invalid {HTTP_MODE_ENV}='{mode}'. Allowed values: {allowed}.",
        )
    return mode


def _assert_real_mode_prerequisites() -> None:
    settings = load_real_settings()

    try:
        with socket.create_connection(
            (settings.postgres.host, settings.postgres.port),
            timeout=2,
        ):
            pass
    except OSError as err:
        raise RuntimeError(
            "HTTP real mode prerequisite failed: cannot connect to database "
            f"{settings.postgres.host}:{settings.postgres.port}. "
            "Make sure DB is up before running BDD_HTTP_MODE=real.",
        ) from err


def _migrate_real_schema() -> None:
    result = subprocess.run(
        ["uv", "run", "alembic", "-c", "alembic.ini", "upgrade", "head"],
        cwd=_BACKEND_DIR,
        env={**os.environ, "APP_ENV": os.environ.get("APP_ENV", "local")},
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "HTTP real mode migration failed: "
            f"{result.stderr.strip() or result.stdout.strip()}",
        )


# ---------------------------------------------------------------------------
# Hooks
# ---------------------------------------------------------------------------
def before_all(context):
    context.mocks = MockRegistry()
    context.http_mode = _resolve_http_mode()
    context.auth_cookies = {"access_token": "fake-test-token"}

    if context.http_mode == "real":
        os.environ.setdefault("APP_ENV", "local")
        _assert_real_mode_prerequisites()
        _migrate_real_schema()
        settings = load_real_settings()
        context.real_fixture_runner = RealFixtureRunner(settings)
        context.app = create_real_test_app()
    else:
        context.app = create_test_app(context.mocks)


def before_scenario(context, scenario):
    if context.http_mode == "mock":
        context.mocks.reset_all()
        context.auth_cookies = {"access_token": "fake-test-token"}
    else:
        context.auth_cookies = context.real_fixture_runner.prepare_scenario()

    context.users = {}
    context.response = None
    context.current_username = None
    context.client = TestClient(context.app)
    context.client.__enter__()

    health = context.client.get("/api/v1/health")
    if health.status_code >= 500:
        raise RuntimeError(
            f"HTTP stage app health check failed: {health.status_code} {health.text}",
        )


def after_scenario(context, scenario):
    client = getattr(context, "client", None)
    if client is not None:
        client.__exit__(None, None, None)
