import { createFileRoute } from '@tanstack/react-router'
import { SurveyForms } from '@/features/survey-forms'

export const Route = createFileRoute('/_authenticated/survey-forms/')({
    component: SurveyForms,
})
