import { createFileRoute } from '@tanstack/react-router'
import { SurveyTemplateEdit } from '@/features/surveys/template-edit'

export const Route = createFileRoute('/_authenticated/surveys/templates/$templateId/edit')({
  component: RouteComponent,
})

// eslint-disable-next-line react-refresh/only-export-components
function RouteComponent() {
  const { templateId } = Route.useParams()
  return <SurveyTemplateEdit templateId={templateId} />
}
