import { createFileRoute } from '@tanstack/react-router'
import { SurveyFill } from '@/features/surveys/survey-fill'

export const Route = createFileRoute(
  '/_authenticated/surveys/assignments/$assignmentId/fill'
)({
  component: RouteComponent,
})

// eslint-disable-next-line react-refresh/only-export-components
function RouteComponent() {
  const { assignmentId } = Route.useParams()
  return <SurveyFill assignmentId={assignmentId} />
}
