from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Final

import httpx
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from real_app import load_real_settings
from real_fixtures import RealFixtureRunner

_FEATURES_DIR = os.path.dirname(os.path.abspath(__file__))
if _FEATURES_DIR not in sys.path:
    sys.path.insert(0, _FEATURES_DIR)

_BASE_URL = "http://127.0.0.1:4173"
_BACKEND_URL = "http://127.0.0.1:8000/openapi.json"
_FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
_WORKSPACE_DIR = Path(__file__).resolve().parents[1]
_SERVER_START_TIMEOUT_SECONDS = 90
UI_MODE_ENV: Final[str] = "BDD_UI_MODE"
UI_MODE_DEFAULT: Final[str] = "mock"
UI_MODE_ALLOWED: Final[set[str]] = {"mock", "dev"}


def _resolve_ui_mode() -> str:
    mode = os.getenv(UI_MODE_ENV, UI_MODE_DEFAULT).strip().lower()
    if mode not in UI_MODE_ALLOWED:
        allowed = ", ".join(sorted(UI_MODE_ALLOWED))
        raise RuntimeError(
            f"Invalid {UI_MODE_ENV}='{mode}'. Allowed values: {allowed}.",
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
            "UI real mode prerequisite failed: cannot connect to database "
            f"{settings.postgres.host}:{settings.postgres.port}. "
            "Make sure DB is up before running BDD_UI_MODE=dev.",
        ) from err


def _migrate_real_schema() -> None:
    result = subprocess.run(
        ["uv", "run", "alembic", "-c", "alembic.ini", "upgrade", "head"],
        cwd=str(_WORKSPACE_DIR / "backend"),
        env={**os.environ, "APP_ENV": os.environ.get("APP_ENV", "local")},
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "UI real mode migration failed: "
            f"{result.stderr.strip() or result.stdout.strip()}",
        )


def _wait_for_server(url: str, timeout_seconds: int) -> None:
    deadline = time.time() + timeout_seconds
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            response = httpx.get(url, timeout=2)
            if response.status_code < 500:
                return
        except Exception as err:  # pragma: no cover - startup polling
            last_error = err
        time.sleep(1)
    if last_error is not None:
        raise RuntimeError(f"UI server did not start in time: {last_error}")
    raise RuntimeError("UI server did not start in time")


def before_all(context):
    context.ui_mode = _resolve_ui_mode()
    frontend_cmd = "dev:mock" if context.ui_mode == "mock" else "dev"

    if context.ui_mode == "dev":
        os.environ.setdefault("APP_ENV", "local")
        _assert_real_mode_prerequisites()
        _migrate_real_schema()
        context.real_fixture_runner = RealFixtureRunner(load_real_settings())
        context.backend_process = subprocess.Popen(
            ["uv", "run", "--project", "backend", "python", "-m", "app.run"],
            cwd=str(_WORKSPACE_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        _wait_for_server(_BACKEND_URL, _SERVER_START_TIMEOUT_SECONDS)

    context.server_process = subprocess.Popen(
        [
            "pnpm",
            "run",
            frontend_cmd,
            "--host",
            "127.0.0.1",
            "--port",
            "4173",
        ],
        cwd=str(_FRONTEND_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    _wait_for_server(_BASE_URL, _SERVER_START_TIMEOUT_SECONDS)

    context.playwright = sync_playwright().start()
    context.browser = context.playwright.chromium.launch(headless=True)


def before_scenario(context, scenario):
    context.ui_state = {
        "template_id": "11111111-1111-1111-1111-111111111111",
        "template_version_id": "21111111-1111-1111-1111-111111111111",
        "assignment_id": "31111111-1111-1111-1111-111111111111",
        "stage_used": None,
        "feature_files": ["survey-assignment-workflow.feature"],
        "last_response": "R1",
    }

    if context.ui_mode == "dev":
        context.auth_cookies = context.real_fixture_runner.prepare_scenario()
        context.ui_state.update(context.real_fixture_runner.baseline_state())
    else:
        context.auth_cookies = {"access_token": "fake-test-token"}

    context.browser_context = context.browser.new_context(base_url=_BASE_URL)
    context.browser_context.add_cookies(
        [
            {
                "name": "access_token",
                "value": context.auth_cookies["access_token"],
                "url": _BASE_URL,
            }
        ],
    )
    context.page = context.browser_context.new_page()


def after_scenario(context, scenario):
    page: Page | None = getattr(context, "page", None)
    if page is not None:
        page.close()

    browser_context: BrowserContext | None = getattr(context, "browser_context", None)
    if browser_context is not None:
        browser_context.close()


def after_all(context):
    browser: Browser | None = getattr(context, "browser", None)
    if browser is not None:
        browser.close()

    playwright = getattr(context, "playwright", None)
    if playwright is not None:
        playwright.stop()

    server_process: subprocess.Popen | None = getattr(context, "server_process", None)
    if server_process is not None and server_process.poll() is None:
        try:
            os.killpg(server_process.pid, signal.SIGTERM)
            server_process.wait(timeout=10)
        except Exception:  # pragma: no cover - cleanup fallback
            os.killpg(server_process.pid, signal.SIGKILL)

    backend_process: subprocess.Popen | None = getattr(context, "backend_process", None)
    if backend_process is not None and backend_process.poll() is None:
        try:
            os.killpg(backend_process.pid, signal.SIGTERM)
            backend_process.wait(timeout=10)
        except Exception:  # pragma: no cover - cleanup fallback
            os.killpg(backend_process.pid, signal.SIGKILL)
