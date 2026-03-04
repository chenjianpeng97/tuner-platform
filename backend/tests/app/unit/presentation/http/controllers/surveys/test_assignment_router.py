from fastapi import FastAPI

from app.presentation.http.controllers.surveys.router import create_surveys_router


def _openapi() -> dict:
    app = FastAPI()
    app.include_router(create_surveys_router(), prefix="/api/v1")
    return app.openapi()


def test_surveys_router_exposes_assignment_endpoints() -> None:
    openapi = _openapi()

    assert "/api/v1/surveys/assignments" in openapi["paths"]
    assert "post" in openapi["paths"]["/api/v1/surveys/assignments"]
    assert "get" in openapi["paths"]["/api/v1/surveys/assignments"]

    assert "/api/v1/surveys/assignments/{assignment_id}" in openapi["paths"]
    assert "get" in openapi["paths"]["/api/v1/surveys/assignments/{assignment_id}"]

    assert "/api/v1/surveys/assignments/{assignment_id}/close" in openapi["paths"]
    assert "post" in openapi["paths"]["/api/v1/surveys/assignments/{assignment_id}/close"]


def test_assignment_endpoints_require_auth_cookie_security() -> None:
    openapi = _openapi()
    operations = [
        openapi["paths"]["/api/v1/surveys/assignments"]["post"],
        openapi["paths"]["/api/v1/surveys/assignments"]["get"],
        openapi["paths"]["/api/v1/surveys/assignments/{assignment_id}"]["get"],
        openapi["paths"]["/api/v1/surveys/assignments/{assignment_id}/close"]["post"],
    ]

    for operation in operations:
        assert operation.get("security"), operation
