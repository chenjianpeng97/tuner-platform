import { createFileRoute } from '@tanstack/react-router'
import { SurveyTemplateList } from '@/features/surveys/template-list'

export const Route = createFileRoute('/_authenticated/surveys/templates/')({
  component: SurveyTemplateList,
})
