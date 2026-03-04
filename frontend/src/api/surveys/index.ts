import { getSurveys } from '@/api/generated/surveys/surveys'
import type {
  CreateSurveyAssignmentRequestPydantic,
  CreateSurveyAssignmentResponse,
  CreateSurveyTemplateRequestPydantic,
  CreateSurveyTemplateResponse,
  MySurveySubmissionQM,
  PublishSurveyTemplateResponse,
  SubmitMySurveySubmissionRequestPydantic,
  SurveyAssignmentDetailQM,
  SurveyAssignmentListItemQM,
  SurveyAssignmentSummaryQM,
  SurveyAuditLogQM,
  SurveySubmissionDetailQM,
  SurveyTemplateDetailQM,
  SurveyTemplateListItemQM,
  UpdateSurveyTemplateRequestPydantic,
} from '@/api/generated/models'

const surveysApi = getSurveys()

export type {
  CreateSurveyAssignmentRequestPydantic,
  CreateSurveyAssignmentResponse,
  CreateSurveyTemplateRequestPydantic,
  CreateSurveyTemplateResponse,
  MySurveySubmissionQM,
  PublishSurveyTemplateResponse,
  SubmitMySurveySubmissionRequestPydantic,
  SurveyAssignmentDetailQM,
  SurveyAssignmentListItemQM,
  SurveyAssignmentSummaryQM,
  SurveyAuditLogQM,
  SurveySubmissionDetailQM,
  SurveyTemplateDetailQM,
  SurveyTemplateListItemQM,
  UpdateSurveyTemplateRequestPydantic,
}

export async function listSurveyTemplates(): Promise<SurveyTemplateListItemQM[]> {
  return surveysApi.listSurveyTemplatesApiV1SurveysTemplatesGet()
}

export async function createSurveyTemplate(
  payload: CreateSurveyTemplateRequestPydantic
): Promise<CreateSurveyTemplateResponse> {
  return surveysApi.createSurveyTemplateApiV1SurveysTemplatesPost(payload)
}

export async function getSurveyTemplate(templateId: string): Promise<SurveyTemplateDetailQM> {
  return surveysApi.getSurveyTemplateApiV1SurveysTemplatesTemplateIdGet(templateId)
}

export async function updateSurveyTemplate(
  templateId: string,
  payload: UpdateSurveyTemplateRequestPydantic
): Promise<void> {
  await surveysApi.updateSurveyTemplateApiV1SurveysTemplatesTemplateIdPatch(
    templateId,
    payload
  )
}

export async function publishSurveyTemplate(
  templateId: string
): Promise<PublishSurveyTemplateResponse> {
  return surveysApi.publishSurveyTemplateApiV1SurveysTemplatesTemplateIdPublishPost(templateId)
}

export async function listSurveyAssignments(): Promise<SurveyAssignmentListItemQM[]> {
  return surveysApi.listSurveyAssignmentsApiV1SurveysAssignmentsGet()
}

export async function createSurveyAssignment(
  payload: CreateSurveyAssignmentRequestPydantic
): Promise<CreateSurveyAssignmentResponse> {
  return surveysApi.createSurveyAssignmentApiV1SurveysAssignmentsPost(payload)
}

export async function getSurveyAssignment(
  assignmentId: string
): Promise<SurveyAssignmentDetailQM> {
  return surveysApi.getSurveyAssignmentApiV1SurveysAssignmentsAssignmentIdGet(assignmentId)
}

export async function closeSurveyAssignment(assignmentId: string): Promise<void> {
  await surveysApi.closeSurveyAssignmentApiV1SurveysAssignmentsAssignmentIdClosePost(
    assignmentId
  )
}

export async function getMySurveySubmission(
  assignmentId: string
): Promise<MySurveySubmissionQM> {
  return surveysApi.getMySurveySubmissionApiV1SurveysAssignmentsAssignmentIdMySubmissionGet(
    assignmentId
  )
}

export async function putMySurveySubmission(
  assignmentId: string,
  payload: SubmitMySurveySubmissionRequestPydantic
): Promise<void> {
  await surveysApi.putMySurveySubmissionApiV1SurveysAssignmentsAssignmentIdMySubmissionPut(
    assignmentId,
    payload
  )
}

export async function getSurveyAssignmentSubmissions(
  assignmentId: string
): Promise<SurveySubmissionDetailQM[]> {
  return surveysApi.getSurveyAssignmentSubmissionsApiV1SurveysAssignmentsAssignmentIdSubmissionsGet(
    assignmentId
  )
}

export async function getSurveyAssignmentSummary(
  assignmentId: string
): Promise<SurveyAssignmentSummaryQM> {
  return surveysApi.getSurveyAssignmentSummaryApiV1SurveysAssignmentsAssignmentIdSummaryGet(
    assignmentId
  )
}

export async function listSurveyAuditLogs(
  fromAt?: string,
  toAt?: string
): Promise<SurveyAuditLogQM[]> {
  return surveysApi.listSurveyAuditLogsApiV1SurveysAuditLogsGet({
    from_at: fromAt,
    to_at: toAt,
  })
}

export async function exportSurveyAuditLogsCsv(
  fromAt?: string,
  toAt?: string
): Promise<string> {
  const data = await surveysApi.exportSurveyAuditLogsApiV1SurveysAuditLogsExportGet({
    from_at: fromAt,
    to_at: toAt,
  })
  return String(data)
}
