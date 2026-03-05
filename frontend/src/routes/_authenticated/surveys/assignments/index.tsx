import { createFileRoute } from '@tanstack/react-router'
import { SurveyAssignmentList } from '@/features/surveys/assignment-list'

export const Route = createFileRoute('/_authenticated/surveys/assignments/')({
    component: SurveyAssignmentList,
})
