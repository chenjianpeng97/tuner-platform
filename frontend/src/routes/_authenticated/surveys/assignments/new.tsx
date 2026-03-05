import { createFileRoute } from '@tanstack/react-router'
import { SurveyAssignmentCreate } from '@/features/surveys/assignment-create'

export const Route = createFileRoute('/_authenticated/surveys/assignments/new')({
    component: SurveyAssignmentCreate,
})
