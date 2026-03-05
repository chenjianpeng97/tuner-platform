import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from '@tanstack/react-router'
import { ChevronRight } from 'lucide-react'
import { toast } from 'sonner'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { ProfileDropdown } from '@/components/profile-dropdown'
import { ThemeSwitch } from '@/components/theme-switch'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
    closeSurveyAssignment,
    getSurveyAssignment,
    getSurveyAssignmentSubmissions,
    type SurveyAssignmentDetailQM,
    type SurveySubmissionDetailQM,
} from '@/api/surveys'

interface Props {
    assignmentId: string
}

export function SurveyAssignmentDetail({ assignmentId }: Props) {
    const queryClient = useQueryClient()

    const { data: assignment, isLoading } = useQuery<SurveyAssignmentDetailQM>({
        queryKey: ['surveys', 'assignments', assignmentId],
        queryFn: () => getSurveyAssignment(assignmentId),
    })

    const { data: submissions = [] } = useQuery<SurveySubmissionDetailQM[]>({
        queryKey: ['surveys', 'assignments', assignmentId, 'submissions'],
        queryFn: () => getSurveyAssignmentSubmissions(assignmentId),
        enabled: Boolean(assignment),
    })

    const closeMutation = useMutation({
        mutationFn: () => closeSurveyAssignment(assignmentId),
        onSuccess: () => {
            toast.success('Assignment closed')
            queryClient.invalidateQueries({ queryKey: ['surveys', 'assignments', assignmentId] })
            queryClient.invalidateQueries({ queryKey: ['surveys', 'assignments'] })
        },
        onError: () => toast.error('Failed to close assignment'),
    })

    if (isLoading) {
        return (
            <>
                <Header>
                    <div className='flex items-center gap-2 ml-auto'>
                        <ThemeSwitch />
                        <ProfileDropdown />
                    </div>
                </Header>
                <Main>
                    <p className='text-muted-foreground text-sm'>Loading...</p>
                </Main>
            </>
        )
    }

    if (!assignment) return null

    const pct = Math.round((assignment.ratio ?? 0) * 100)
    const submittedIds = new Set(submissions.map((s) => s.assignee_user_id))
    const isInProgress = assignment.status === 'in_progress'

    return (
        <>
            <Header>
                <div className='flex items-center gap-2 ml-auto'>
                    <ThemeSwitch />
                    <ProfileDropdown />
                </div>
            </Header>

            <Main>
                {/* Breadcrumb */}
                <nav className='mb-6 flex items-center gap-1 text-sm text-muted-foreground'>
                    <Link to='/surveys/assignments' className='hover:text-foreground transition-colors'>
                        Assignments
                    </Link>
                    <ChevronRight className='h-4 w-4' />
                    <span className='text-foreground font-medium'>{assignmentId.slice(0, 8)}</span>
                </nav>

                {/* Progress board */}
                <Card className='mb-6'>
                    <CardHeader>
                        <div className='flex items-start justify-between'>
                            <div>
                                <CardTitle>Assignment Progress</CardTitle>
                                <CardDescription className='mt-1'>
                                    Version: {assignment.template_version_id.slice(0, 8)}
                                </CardDescription>
                            </div>
                            <div className='flex items-center gap-3'>
                                <Badge variant={isInProgress ? 'secondary' : 'default'}>
                                    {isInProgress ? 'In Progress' : 'Completed'}
                                </Badge>
                                {isInProgress && (
                                    <Button
                                        variant='destructive'
                                        size='sm'
                                        onClick={() => closeMutation.mutate()}
                                        disabled={closeMutation.isPending}
                                    >
                                        Close
                                    </Button>
                                )}
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent className='space-y-3'>
                        <div className='flex items-center gap-4'>
                            <span className='text-4xl font-bold'>{pct}%</span>
                            <div className='flex-1'>
                                <div className='flex justify-between text-sm text-muted-foreground mb-1'>
                                    <span>Submitted</span>
                                    <span>
                                        {assignment.submitted_count} / {assignment.assignee_count}
                                    </span>
                                </div>
                                <Progress value={pct} className='h-3' />
                            </div>
                        </div>
                        {assignment.due_at && (
                            <p className='text-sm text-muted-foreground'>
                                Due: {new Date(assignment.due_at).toLocaleString()}
                            </p>
                        )}
                    </CardContent>
                </Card>

                {/* Tabs */}
                <Tabs defaultValue='participants'>
                    <TabsList>
                        <TabsTrigger value='participants'>Participants</TabsTrigger>
                        <TabsTrigger value='results'>Results</TabsTrigger>
                    </TabsList>

                    <TabsContent value='participants' className='mt-4'>
                        <div className='rounded-md border'>
                            <Table>
                                <TableHeader>
                                    <TableRow>
                                        <TableHead>User ID</TableHead>
                                        <TableHead>Status</TableHead>
                                        <TableHead>Submitted At</TableHead>
                                        <TableHead />
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {(assignment.assignee_user_ids ?? []).map((userId) => {
                                        const sub = submissions.find((s) => s.assignee_user_id === userId)
                                        const hasSubmitted = submittedIds.has(userId)
                                        return (
                                            <TableRow key={userId}>
                                                <TableCell className='font-mono text-xs'>{userId.slice(0, 8)}</TableCell>
                                                <TableCell>
                                                    <Badge variant={hasSubmitted ? 'default' : 'outline'}>
                                                        {hasSubmitted ? 'Submitted' : 'Pending'}
                                                    </Badge>
                                                </TableCell>
                                                <TableCell className='text-sm text-muted-foreground'>
                                                    {sub?.submitted_at
                                                        ? new Date(sub.submitted_at).toLocaleString()
                                                        : '—'}
                                                </TableCell>
                                                <TableCell className='text-right'>
                                                    {isInProgress && !hasSubmitted && (
                                                        <Button variant='outline' size='sm' asChild>
                                                            <Link
                                                                to='/surveys/assignments/$assignmentId/fill'
                                                                params={{ assignmentId }}
                                                            >
                                                                Fill Survey
                                                            </Link>
                                                        </Button>
                                                    )}
                                                </TableCell>
                                            </TableRow>
                                        )
                                    })}
                                </TableBody>
                            </Table>
                        </div>
                    </TabsContent>

                    <TabsContent value='results' className='mt-4'>
                        <Card>
                            <CardContent className='pt-6'>
                                <p className='text-muted-foreground text-sm mb-4'>
                                    View aggregated responses and individual answers.
                                </p>
                                <Button asChild>
                                    <Link
                                        to='/surveys/assignments/$assignmentId/results'
                                        params={{ assignmentId }}
                                    >
                                        Open Results
                                    </Link>
                                </Button>
                            </CardContent>
                        </Card>
                    </TabsContent>
                </Tabs>
            </Main>
        </>
    )
}
