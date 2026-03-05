"""Real HTTP-stage application factory.

Builds the production FastAPI app (real DI bindings) for Behave HTTP-stage
integration runs.
"""

from __future__ import annotations

from fastapi import FastAPI

from app.run import make_app
from app.setup.config.settings import AppSettings, load_settings


def load_real_settings() -> AppSettings:
    return load_settings()


def create_real_test_app() -> FastAPI:
    settings = load_real_settings()
    return make_app(settings=settings)
