from fastapi import FastAPI

from app.presentation.http.controllers.surveys.router import create_surveys_router


def _openapi() -> dict:
    app = FastAPI()
    app.include_router(create_surveys_router(), prefix="/api/v1")
    return app.openapi()


def test_surveys_router_exposes_result_endpoints() -> None:
    openapi = _openapi()

    assert "/api/v1/surveys/assignments/{assignment_id}/submissions" in openapi["paths"]
    assert (
        "get" in openapi["paths"]["/api/v1/surveys/assignments/{assignment_id}/submissions"]
    )

    assert "/api/v1/surveys/assignments/{assignment_id}/summary" in openapi["paths"]
    assert "get" in openapi["paths"]["/api/v1/surveys/assignments/{assignment_id}/summary"]


def test_result_endpoints_require_auth_cookie_security() -> None:
    openapi = _openapi()
    operations = [
        openapi["paths"]["/api/v1/surveys/assignments/{assignment_id}/submissions"][
            "get"
        ],
        openapi["paths"]["/api/v1/surveys/assignments/{assignment_id}/summary"]["get"],
    ]

    for operation in operations:
        assert operation.get("security"), operation
