import { createFileRoute } from '@tanstack/react-router'
import { SurveyAssignmentDetail } from '@/features/surveys/assignment-detail'

export const Route = createFileRoute('/_authenticated/surveys/assignments/$assignmentId/')({
    component: RouteComponent,
})

// eslint-disable-next-line react-refresh/only-export-components
function RouteComponent() {
    const { assignmentId } = Route.useParams()
    return <SurveyAssignmentDetail assignmentId={assignmentId} />
}
