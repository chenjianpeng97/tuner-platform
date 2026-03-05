from dishka import Provider, Scope, provide, provide_all

from app.application.commands.activate_user import ActivateUserInteractor
from app.application.commands.create_user import CreateUserInteractor
from app.application.commands.create_survey_template import (
    CreateSurveyTemplateInteractor,
)
from app.application.commands.create_survey_assignment import (
    CreateSurveyAssignmentInteractor,
)
from app.application.commands.deactivate_user import DeactivateUserInteractor
from app.application.commands.grant_admin import GrantAdminInteractor
from app.application.commands.publish_survey_template import (
    PublishSurveyTemplateInteractor,
)
from app.application.commands.submit_my_survey_submission import (
    SubmitMySurveySubmissionInteractor,
)
from app.application.commands.close_survey_assignment import (
    CloseSurveyAssignmentInteractor,
)
from app.application.commands.revoke_admin import RevokeAdminInteractor
from app.application.commands.set_user_password import SetUserPasswordInteractor
from app.application.commands.update_survey_template import (
    UpdateSurveyTemplateInteractor,
)
from app.application.common.ports.access_revoker import AccessRevoker
from app.application.common.ports.flusher import Flusher
from app.application.common.ports.identity_provider import IdentityProvider
from app.application.common.ports.survey_audit_command_gateway import (
    SurveyAuditCommandGateway,
)
from app.application.common.ports.survey_audit_query_gateway import (
    SurveyAuditQueryGateway,
)
from app.application.common.ports.survey_query_gateway import SurveyQueryGateway
from app.application.common.ports.survey_assignment_command_gateway import (
    SurveyAssignmentCommandGateway,
)
from app.application.common.ports.survey_template_command_gateway import (
    SurveyTemplateCommandGateway,
)
from app.application.common.ports.transaction_manager import (
    TransactionManager,
)
from app.application.common.ports.user_command_gateway import UserCommandGateway
from app.application.common.ports.user_query_gateway import UserQueryGateway
from app.application.common.services.current_user import CurrentUserService
from app.application.queries.get_survey_template import GetSurveyTemplateQueryService
from app.application.queries.get_survey_assignment import (
    GetSurveyAssignmentQueryService,
)
from app.application.queries.get_survey_assignment_submissions import (
    GetSurveyAssignmentSubmissionsQueryService,
)
from app.application.queries.get_survey_assignment_summary import (
    GetSurveyAssignmentSummaryQueryService,
)
from app.application.queries.get_my_survey_submission import (
    GetMySurveySubmissionQueryService,
)
from app.application.queries.list_survey_assignments import (
    ListSurveyAssignmentsQueryService,
)
from app.application.queries.list_survey_templates import (
    ListSurveyTemplatesQueryService,
)
from app.application.queries.list_survey_audit_logs import (
    ExportSurveyAuditLogsCsvQueryService,
    ListSurveyAuditLogsQueryService,
)
from app.application.queries.list_users import ListUsersQueryService
from app.infrastructure.adapters.main_flusher_sqla import SqlaMainFlusher
from app.infrastructure.adapters.main_transaction_manager_sqla import (
    SqlaMainTransactionManager,
)
from app.infrastructure.adapters.survey_reader_sqla import SqlaSurveyReader
from app.infrastructure.adapters.survey_audit_reader_sqla import SqlaSurveyAuditReader
from app.infrastructure.adapters.survey_audit_writer_sqla import SqlaSurveyAuditWriter
from app.infrastructure.adapters.survey_assignment_data_mapper_sqla import (
    SqlaSurveyAssignmentDataMapper,
)
from app.infrastructure.adapters.survey_template_data_mapper_sqla import (
    SqlaSurveyTemplateDataMapper,
)
from app.infrastructure.adapters.user_data_mapper_sqla import (
    SqlaUserDataMapper,
)
from app.infrastructure.adapters.user_reader_sqla import SqlaUserReader
from app.infrastructure.auth.adapters.access_revoker import (
    AuthSessionAccessRevoker,
)
from app.infrastructure.auth.adapters.identity_provider import (
    AuthSessionIdentityProvider,
)


class ApplicationProvider(Provider):
    scope = Scope.REQUEST

    # Services
    services = provide_all(
        CurrentUserService,
    )

    # Ports Persistence
    tx_manager = provide(SqlaMainTransactionManager, provides=TransactionManager)
    flusher = provide(SqlaMainFlusher, provides=Flusher)
    user_command_gateway = provide(SqlaUserDataMapper, provides=UserCommandGateway)
    user_query_gateway = provide(SqlaUserReader, provides=UserQueryGateway)
    survey_template_command_gateway = provide(
        SqlaSurveyTemplateDataMapper, provides=SurveyTemplateCommandGateway
    )
    survey_assignment_command_gateway = provide(
        SqlaSurveyAssignmentDataMapper, provides=SurveyAssignmentCommandGateway
    )
    survey_audit_command_gateway = provide(
        SqlaSurveyAuditWriter, provides=SurveyAuditCommandGateway
    )
    survey_audit_query_gateway = provide(
        SqlaSurveyAuditReader, provides=SurveyAuditQueryGateway
    )
    survey_query_gateway = provide(SqlaSurveyReader, provides=SurveyQueryGateway)

    # Ports Auth
    access_revoker = provide(AuthSessionAccessRevoker, provides=AccessRevoker)
    identity_provider = provide(AuthSessionIdentityProvider, provides=IdentityProvider)

    # Commands
    commands = provide_all(
        ActivateUserInteractor,
        SetUserPasswordInteractor,
        CreateUserInteractor,
        DeactivateUserInteractor,
        GrantAdminInteractor,
        RevokeAdminInteractor,
        CreateSurveyTemplateInteractor,
        UpdateSurveyTemplateInteractor,
        PublishSurveyTemplateInteractor,
        CreateSurveyAssignmentInteractor,
        CloseSurveyAssignmentInteractor,
        SubmitMySurveySubmissionInteractor,
    )

    # Queries
    query_services = provide_all(
        ListUsersQueryService,
        ListSurveyTemplatesQueryService,
        GetSurveyTemplateQueryService,
        ListSurveyAssignmentsQueryService,
        GetSurveyAssignmentQueryService,
        GetMySurveySubmissionQueryService,
        GetSurveyAssignmentSubmissionsQueryService,
        GetSurveyAssignmentSummaryQueryService,
        ListSurveyAuditLogsQueryService,
        ExportSurveyAuditLogsCsvQueryService,
    )
