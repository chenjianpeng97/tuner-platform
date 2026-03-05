from fastapi import FastAPI

from app.presentation.http.controllers.surveys.router import create_surveys_router


def _openapi() -> dict:
    app = FastAPI()
    app.include_router(create_surveys_router(), prefix="/api/v1")
    return app.openapi()


def test_surveys_router_exposes_template_endpoints() -> None:
    openapi = _openapi()

    assert "/api/v1/surveys/templates" in openapi["paths"]
    assert "post" in openapi["paths"]["/api/v1/surveys/templates"]
    assert "get" in openapi["paths"]["/api/v1/surveys/templates"]
    assert "/api/v1/surveys/templates/{template_id}" in openapi["paths"]
    assert "get" in openapi["paths"]["/api/v1/surveys/templates/{template_id}"]
    assert "patch" in openapi["paths"]["/api/v1/surveys/templates/{template_id}"]
    assert "/api/v1/surveys/templates/{template_id}/publish" in openapi["paths"]
    assert "post" in openapi["paths"]["/api/v1/surveys/templates/{template_id}/publish"]


def test_all_template_endpoints_require_auth_cookie_security() -> None:
    openapi = _openapi()

    operations = [
        openapi["paths"]["/api/v1/surveys/templates"]["post"],
        openapi["paths"]["/api/v1/surveys/templates"]["get"],
        openapi["paths"]["/api/v1/surveys/templates/{template_id}"]["get"],
        openapi["paths"]["/api/v1/surveys/templates/{template_id}"]["patch"],
        openapi["paths"]["/api/v1/surveys/templates/{template_id}/publish"]["post"],
    ]

    for operation in operations:
        assert operation.get("security"), operation
