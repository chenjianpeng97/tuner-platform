from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import httpx
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

_FEATURES_DIR = os.path.dirname(os.path.abspath(__file__))
if _FEATURES_DIR not in sys.path:
    sys.path.insert(0, _FEATURES_DIR)

_BASE_URL = "http://127.0.0.1:4173"
_FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
_SERVER_START_TIMEOUT_SECONDS = 90


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
    context.server_process = subprocess.Popen(
        [
            "pnpm",
            "run",
            "dev:mock",
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
    context.browser_context = context.browser.new_context(base_url=_BASE_URL)
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
