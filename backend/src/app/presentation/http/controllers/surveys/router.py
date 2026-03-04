from fastapi import APIRouter

from app.presentation.http.controllers.surveys.close_assignment import (
    create_close_survey_assignment_router,
)
from app.presentation.http.controllers.surveys.create_assignment import (
    create_create_survey_assignment_router,
)
from app.presentation.http.controllers.surveys.create_template import (
    create_create_survey_template_router,
)
from app.presentation.http.controllers.surveys.get_assignment import (
    create_get_survey_assignment_router,
)
from app.presentation.http.controllers.surveys.get_assignment_submissions import (
    create_get_survey_assignment_submissions_router,
)
from app.presentation.http.controllers.surveys.get_assignment_summary import (
    create_get_survey_assignment_summary_router,
)
from app.presentation.http.controllers.surveys.get_my_submission import (
    create_get_my_survey_submission_router,
)
from app.presentation.http.controllers.surveys.get_template import (
    create_get_survey_template_router,
)
from app.presentation.http.controllers.surveys.list_assignments import (
    create_list_survey_assignments_router,
)
from app.presentation.http.controllers.surveys.list_audit_logs import (
    create_list_survey_audit_logs_router,
)
from app.presentation.http.controllers.surveys.list_templates import (
    create_list_survey_templates_router,
)
from app.presentation.http.controllers.surveys.export_audit_logs import (
    create_export_survey_audit_logs_router,
)
from app.presentation.http.controllers.surveys.publish_template import (
    create_publish_survey_template_router,
)
from app.presentation.http.controllers.surveys.put_my_submission import (
    create_put_my_survey_submission_router,
)
from app.presentation.http.controllers.surveys.update_template import (
    create_update_survey_template_router,
)


def create_surveys_router() -> APIRouter:
    router = APIRouter(
        prefix="/surveys",
        tags=["Surveys"],
    )
    router.include_router(create_create_survey_template_router())
    router.include_router(create_list_survey_templates_router())
    router.include_router(create_get_survey_template_router())
    router.include_router(create_update_survey_template_router())
    router.include_router(create_publish_survey_template_router())
    router.include_router(create_create_survey_assignment_router())
    router.include_router(create_list_survey_assignments_router())
    router.include_router(create_get_survey_assignment_router())
    router.include_router(create_close_survey_assignment_router())
    router.include_router(create_get_my_survey_submission_router())
    router.include_router(create_put_my_survey_submission_router())
    router.include_router(create_get_survey_assignment_submissions_router())
    router.include_router(create_get_survey_assignment_summary_router())
    router.include_router(create_list_survey_audit_logs_router())
    router.include_router(create_export_survey_audit_logs_router())
    return router
