import { createFileRoute } from '@tanstack/react-router'
import { SurveyResults } from '@/features/surveys/survey-results'

export const Route = createFileRoute(
  '/_authenticated/surveys/assignments/$assignmentId/results'
)({
  component: RouteComponent,
})

// eslint-disable-next-line react-refresh/only-export-components
function RouteComponent() {
  const { assignmentId } = Route.useParams()
  return <SurveyResults assignmentId={assignmentId} />
}
