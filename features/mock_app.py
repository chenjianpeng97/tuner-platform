"""
Test application factory with mocked interactors / handlers.

Builds a FastAPI application with the **same routes, middleware, and
error maps** as the production app, but replaces every Dishka-injected
interactor / handler with a ``unittest.mock.AsyncMock``.

No database, auth infrastructure, or external services required.
Only presentation-layer dependencies are needed:
``fastapi``, ``dishka``, ``fastapi-error-map``, ``httpx``.
"""

from __future__ import annotations

from unittest.mock import AsyncMock

from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from app.application.commands.activate_user import ActivateUserInteractor
from app.application.commands.close_survey_assignment import (
    CloseSurveyAssignmentInteractor,
)
from app.application.commands.create_survey_assignment import (
    CreateSurveyAssignmentInteractor,
)
from app.application.commands.create_survey_template import (
    CreateSurveyTemplateInteractor,
)
from app.application.commands.create_user import CreateUserInteractor
from app.application.commands.deactivate_user import DeactivateUserInteractor
from app.application.commands.grant_admin import GrantAdminInteractor
from app.application.commands.publish_survey_template import (
    PublishSurveyTemplateInteractor,
)
from app.application.commands.revoke_admin import RevokeAdminInteractor
from app.application.commands.set_user_password import SetUserPasswordInteractor
from app.application.commands.submit_my_survey_submission import (
    SubmitMySurveySubmissionInteractor,
)
from app.application.commands.update_survey_template import (
    UpdateSurveyTemplateInteractor,
)
from app.application.queries.get_my_survey_submission import (
    GetMySurveySubmissionQueryService,
)
from app.application.queries.get_survey_assignment import (
    GetSurveyAssignmentQueryService,
)
from app.application.queries.get_survey_assignment_submissions import (
    GetSurveyAssignmentSubmissionsQueryService,
)
from app.application.queries.get_survey_assignment_summary import (
    GetSurveyAssignmentSummaryQueryService,
)
from app.application.queries.get_survey_template import GetSurveyTemplateQueryService
from app.application.queries.list_survey_assignments import (
    ListSurveyAssignmentsQueryService,
)
from app.application.queries.list_survey_audit_logs import (
    ExportSurveyAuditLogsCsvQueryService,
    ListSurveyAuditLogsQueryService,
)
from app.application.queries.list_survey_templates import (
    ListSurveyTemplatesQueryService,
)
from app.application.queries.list_users import ListUsersQueryService
from app.infrastructure.auth.handlers.change_password import ChangePasswordHandler
from app.infrastructure.auth.handlers.log_in import LogInHandler
from app.infrastructure.auth.handlers.log_out import LogOutHandler
from app.infrastructure.auth.handlers.sign_up import SignUpHandler
from app.presentation.http.auth.asgi_middleware import ASGIAuthMiddleware
from app.presentation.http.controllers.root_router import create_root_router


class MockRegistry:
    """Holds ``AsyncMock`` instances for every Dishka-provided type.

    The mock provider reads from this registry at dependency-resolution time,
    so reassigning an attribute here immediately affects subsequent requests.

    Call :meth:`reset_all` in ``before_scenario`` to recreate every mock.
    """

    def __init__(self) -> None:
        self._init_mocks()

    # noinspection PyAttributeOutsideInit
    def _init_mocks(self) -> None:
        # Application commands
        self.create_user: AsyncMock = AsyncMock()
        self.activate_user: AsyncMock = AsyncMock()
        self.deactivate_user: AsyncMock = AsyncMock()
        self.grant_admin: AsyncMock = AsyncMock()
        self.revoke_admin: AsyncMock = AsyncMock()
        self.set_user_password: AsyncMock = AsyncMock()
        self.create_survey_template: AsyncMock = AsyncMock()
        self.update_survey_template: AsyncMock = AsyncMock()
        self.publish_survey_template: AsyncMock = AsyncMock()
        self.create_survey_assignment: AsyncMock = AsyncMock()
        self.close_survey_assignment: AsyncMock = AsyncMock()
        self.submit_my_survey_submission: AsyncMock = AsyncMock()

        # Application queries
        self.list_users: AsyncMock = AsyncMock()
        self.list_survey_templates: AsyncMock = AsyncMock()
        self.get_survey_template: AsyncMock = AsyncMock()
        self.list_survey_assignments: AsyncMock = AsyncMock()
        self.get_survey_assignment: AsyncMock = AsyncMock()
        self.get_my_survey_submission: AsyncMock = AsyncMock()
        self.get_survey_assignment_submissions: AsyncMock = AsyncMock()
        self.get_survey_assignment_summary: AsyncMock = AsyncMock()
        self.list_survey_audit_logs: AsyncMock = AsyncMock()
        self.export_survey_audit_logs: AsyncMock = AsyncMock()

        # Infrastructure auth handlers
        self.sign_up: AsyncMock = AsyncMock()
        self.log_in: AsyncMock = AsyncMock()
        self.change_password: AsyncMock = AsyncMock()
        self.log_out: AsyncMock = AsyncMock()

    def reset_all(self) -> None:
        """Recreate every mock to a pristine state."""
        self._init_mocks()


class _MockProvider(Provider):
    """Dishka provider that resolves each interactor / handler type to a mock."""

    scope = Scope.REQUEST

    def __init__(self, registry: MockRegistry) -> None:
        super().__init__()
        self._r = registry

    @provide
    def create_user_interactor(self) -> CreateUserInteractor:
        return self._r.create_user  # type: ignore[return-value]

    @provide
    def activate_user_interactor(self) -> ActivateUserInteractor:
        return self._r.activate_user  # type: ignore[return-value]

    @provide
    def deactivate_user_interactor(self) -> DeactivateUserInteractor:
        return self._r.deactivate_user  # type: ignore[return-value]

    @provide
    def grant_admin_interactor(self) -> GrantAdminInteractor:
        return self._r.grant_admin  # type: ignore[return-value]

    @provide
    def revoke_admin_interactor(self) -> RevokeAdminInteractor:
        return self._r.revoke_admin  # type: ignore[return-value]

    @provide
    def set_user_password_interactor(self) -> SetUserPasswordInteractor:
        return self._r.set_user_password  # type: ignore[return-value]

    @provide
    def create_survey_template_interactor(self) -> CreateSurveyTemplateInteractor:
        return self._r.create_survey_template  # type: ignore[return-value]

    @provide
    def update_survey_template_interactor(self) -> UpdateSurveyTemplateInteractor:
        return self._r.update_survey_template  # type: ignore[return-value]

    @provide
    def publish_survey_template_interactor(self) -> PublishSurveyTemplateInteractor:
        return self._r.publish_survey_template  # type: ignore[return-value]

    @provide
    def create_survey_assignment_interactor(self) -> CreateSurveyAssignmentInteractor:
        return self._r.create_survey_assignment  # type: ignore[return-value]

    @provide
    def close_survey_assignment_interactor(self) -> CloseSurveyAssignmentInteractor:
        return self._r.close_survey_assignment  # type: ignore[return-value]

    @provide
    def submit_my_survey_submission_interactor(self) -> SubmitMySurveySubmissionInteractor:
        return self._r.submit_my_survey_submission  # type: ignore[return-value]

    @provide
    def list_users_query_service(self) -> ListUsersQueryService:
        return self._r.list_users  # type: ignore[return-value]

    @provide
    def list_survey_templates_query_service(self) -> ListSurveyTemplatesQueryService:
        return self._r.list_survey_templates  # type: ignore[return-value]

    @provide
    def get_survey_template_query_service(self) -> GetSurveyTemplateQueryService:
        return self._r.get_survey_template  # type: ignore[return-value]

    @provide
    def list_survey_assignments_query_service(self) -> ListSurveyAssignmentsQueryService:
        return self._r.list_survey_assignments  # type: ignore[return-value]

    @provide
    def get_survey_assignment_query_service(self) -> GetSurveyAssignmentQueryService:
        return self._r.get_survey_assignment  # type: ignore[return-value]

    @provide
    def get_my_survey_submission_query_service(self) -> GetMySurveySubmissionQueryService:
        return self._r.get_my_survey_submission  # type: ignore[return-value]

    @provide
    def get_survey_assignment_submissions_query_service(
        self,
    ) -> GetSurveyAssignmentSubmissionsQueryService:
        return self._r.get_survey_assignment_submissions  # type: ignore[return-value]

    @provide
    def get_survey_assignment_summary_query_service(
        self,
    ) -> GetSurveyAssignmentSummaryQueryService:
        return self._r.get_survey_assignment_summary  # type: ignore[return-value]

    @provide
    def list_survey_audit_logs_query_service(self) -> ListSurveyAuditLogsQueryService:
        return self._r.list_survey_audit_logs  # type: ignore[return-value]

    @provide
    def export_survey_audit_logs_query_service(self) -> ExportSurveyAuditLogsCsvQueryService:
        return self._r.export_survey_audit_logs  # type: ignore[return-value]

    @provide
    def sign_up_handler(self) -> SignUpHandler:
        return self._r.sign_up  # type: ignore[return-value]

    @provide
    def log_in_handler(self) -> LogInHandler:
        return self._r.log_in  # type: ignore[return-value]

    @provide
    def change_password_handler(self) -> ChangePasswordHandler:
        return self._r.change_password  # type: ignore[return-value]

    @provide
    def log_out_handler(self) -> LogOutHandler:
        return self._r.log_out  # type: ignore[return-value]


def create_test_app(registry: MockRegistry) -> FastAPI:
    """Build a FastAPI app with production routes but mocked DI.

    * No lifespan (no ``map_tables()``, no database connection).
    * ``ASGIAuthMiddleware`` is kept (it only handles cookie I/O).
    * All routes are registered so that 404 behaviour is realistic.
    """
    app = FastAPI()
    app.add_middleware(ASGIAuthMiddleware)
    app.include_router(create_root_router())

    container = make_async_container(_MockProvider(registry))
    setup_dishka(container, app)

    return app
