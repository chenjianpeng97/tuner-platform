import { createFileRoute } from '@tanstack/react-router'
import { SurveyAssignmentWorkflow } from '@/features/survey-assignment'

export const Route = createFileRoute('/_authenticated/survey-forms/')({
    component: SurveyAssignmentWorkflow,
})
