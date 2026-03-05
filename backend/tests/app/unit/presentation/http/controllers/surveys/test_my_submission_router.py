from fastapi import FastAPI

from app.presentation.http.controllers.surveys.router import create_surveys_router


def _openapi() -> dict:
    app = FastAPI()
    app.include_router(create_surveys_router(), prefix="/api/v1")
    return app.openapi()


def test_surveys_router_exposes_my_submission_endpoints() -> None:
    openapi = _openapi()

    assert "/api/v1/surveys/assignments/{assignment_id}/my-submission" in openapi["paths"]
    assert (
        "get"
        in openapi["paths"]["/api/v1/surveys/assignments/{assignment_id}/my-submission"]
    )
    assert (
        "put"
        in openapi["paths"]["/api/v1/surveys/assignments/{assignment_id}/my-submission"]
    )


def test_my_submission_endpoints_require_auth_cookie_security() -> None:
    openapi = _openapi()
    operations = [
        openapi["paths"]["/api/v1/surveys/assignments/{assignment_id}/my-submission"][
            "get"
        ],
        openapi["paths"]["/api/v1/surveys/assignments/{assignment_id}/my-submission"][
            "put"
        ],
    ]

    for operation in operations:
        assert operation.get("security"), operation
