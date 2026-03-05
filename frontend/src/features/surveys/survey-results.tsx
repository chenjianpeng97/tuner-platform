import { useQuery } from '@tanstack/react-query'
import { Link } from '@tanstack/react-router'
import { ChevronRight, Download } from 'lucide-react'
import { toast } from 'sonner'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { ProfileDropdown } from '@/components/profile-dropdown'
import { ThemeSwitch } from '@/components/theme-switch'
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
    exportSurveyAuditLogsCsv,
    getSurveyAssignment,
    getSurveyAssignmentSubmissions,
    getSurveyAssignmentSummary,
    getSurveyTemplate,
    listSurveyTemplates,
    type SurveyAssignmentDetailQM,
    type SurveyAssignmentSummaryQM,
    type SurveySubmissionDetailQM,
    type SurveyTemplateDetailQM,
} from '@/api/surveys'

interface Props {
    assignmentId: string
}

export function SurveyResults({ assignmentId }: Props) {
    const { data: assignment } = useQuery<SurveyAssignmentDetailQM>({
        queryKey: ['surveys', 'assignments', assignmentId],
        queryFn: () => getSurveyAssignment(assignmentId),
    })

    const { data: submissions = [] } = useQuery<SurveySubmissionDetailQM[]>({
        queryKey: ['surveys', 'assignments', assignmentId, 'submissions'],
        queryFn: () => getSurveyAssignmentSubmissions(assignmentId),
    })

    const { data: summary } = useQuery<SurveyAssignmentSummaryQM>({
        queryKey: ['surveys', 'assignments', assignmentId, 'summary'],
        queryFn: () => getSurveyAssignmentSummary(assignmentId),
    })

    const { data: templates = [] } = useQuery({
        queryKey: ['surveys', 'templates'],
        queryFn: listSurveyTemplates,
    })

    const templateId = templates.find(
        (t) => t.latest_published_version_id === assignment?.template_version_id
    )?.id_

    const { data: template } = useQuery<SurveyTemplateDetailQM>({
        queryKey: ['surveys', 'templates', templateId],
        queryFn: () => getSurveyTemplate(templateId!),
        enabled: Boolean(templateId),
    })

    async function handleExportCsv() {
        try {
            const csv = await exportSurveyAuditLogsCsv()
            const blob = new Blob([csv], { type: 'text/csv' })
            const url = URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = `survey-audit-${assignmentId.slice(0, 8)}.csv`
            a.click()
            URL.revokeObjectURL(url)
        } catch {
            toast.error('Failed to export CSV')
        }
    }

    const questions = template?.questions ?? []
    const choiceCounts = (summary?.choice_counts ?? {}) as Record<string, Record<string, number>>
    const textAnswers = (summary?.text_answers ?? {}) as Record<string, string[]>

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
                    <Link
                        to='/surveys/assignments/$assignmentId'
                        params={{ assignmentId }}
                        className='hover:text-foreground transition-colors'
                    >
                        {assignmentId.slice(0, 8)}
                    </Link>
                    <ChevronRight className='h-4 w-4' />
                    <span className='text-foreground font-medium'>Results</span>
                </nav>

                <div className='mb-6 flex items-center justify-between'>
                    <h1 className='text-2xl font-bold'>Survey Results</h1>
                    <Button variant='outline' onClick={handleExportCsv}>
                        <Download className='mr-2 h-4 w-4' />
                        Export CSV
                    </Button>
                </div>

                <Tabs defaultValue='by-participant'>
                    <TabsList>
                        <TabsTrigger value='by-participant'>By Participant</TabsTrigger>
                        <TabsTrigger value='summary'>Summary by Question</TabsTrigger>
                    </TabsList>

                    {/* By Participant tab */}
                    <TabsContent value='by-participant' className='mt-4'>
                        {submissions.length === 0 ? (
                            <p className='text-muted-foreground text-sm'>No submissions yet.</p>
                        ) : (
                            <div className='rounded-md border'>
                                <Table>
                                    <TableHeader>
                                        <TableRow>
                                            <TableHead>Participant</TableHead>
                                            <TableHead>Submitted At</TableHead>
                                            {questions.map((q) => (
                                                <TableHead key={q.key}>{q.title}</TableHead>
                                            ))}
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {submissions.map((sub) => (
                                            <TableRow key={sub.assignee_user_id}>
                                                <TableCell className='font-mono text-xs'>
                                                    {sub.assignee_user_id.slice(0, 8)}
                                                </TableCell>
                                                <TableCell className='text-sm text-muted-foreground'>
                                                    {sub.submitted_at
                                                        ? new Date(sub.submitted_at).toLocaleString()
                                                        : '—'}
                                                </TableCell>
                                                {questions.map((q) => {
                                                    const a = (sub.answers as Record<string, unknown>)?.[q.key]
                                                    const display = Array.isArray(a) ? a.join(', ') : String(a ?? '—')
                                                    return (
                                                        <TableCell key={q.key} className='text-sm'>
                                                            {display}
                                                        </TableCell>
                                                    )
                                                })}
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </div>
                        )}
                    </TabsContent>

                    {/* Summary by Question tab */}
                    <TabsContent value='summary' className='mt-4 space-y-6'>
                        {questions.length === 0 && (
                            <p className='text-muted-foreground text-sm'>Loading questions...</p>
                        )}
                        {questions.map((q) => {
                            if (q.question_type === 'text') {
                                const answers = textAnswers[q.key] ?? []
                                return (
                                    <Card key={q.key}>
                                        <CardHeader>
                                            <CardTitle className='text-base'>{q.title}</CardTitle>
                                            <CardDescription>Text responses ({answers.length})</CardDescription>
                                        </CardHeader>
                                        <CardContent className='space-y-2'>
                                            {answers.length === 0 ? (
                                                <p className='text-muted-foreground text-sm'>No responses.</p>
                                            ) : (
                                                answers.map((answer, i) => (
                                                    <div
                                                        key={i}
                                                        className='rounded-md bg-muted px-3 py-2 text-sm'
                                                    >
                                                        {answer}
                                                    </div>
                                                ))
                                            )}
                                        </CardContent>
                                    </Card>
                                )
                            }

                            const counts = choiceCounts[q.key] ?? {}
                            const total = Object.values(counts).reduce((s, n) => s + n, 0)

                            return (
                                <Card key={q.key}>
                                    <CardHeader>
                                        <CardTitle className='text-base'>{q.title}</CardTitle>
                                        <CardDescription>
                                            {q.question_type === 'multi_choice' ? 'Multiple choice' : 'Single choice'}{' '}
                                            — {total} response{total !== 1 ? 's' : ''}
                                        </CardDescription>
                                    </CardHeader>
                                    <CardContent className='space-y-3'>
                                        {(q.options ?? []).map((opt) => {
                                            const count = counts[opt] ?? 0
                                            const pct = total > 0 ? Math.round((count / total) * 100) : 0
                                            return (
                                                <div key={opt} className='space-y-1'>
                                                    <div className='flex items-center justify-between text-sm'>
                                                        <span>{opt}</span>
                                                        <span className='text-muted-foreground'>
                                                            {count} ({pct}%)
                                                        </span>
                                                    </div>
                                                    <Progress value={pct} className='h-2' />
                                                </div>
                                            )
                                        })}
                                    </CardContent>
                                </Card>
                            )
                        })}
                    </TabsContent>
                </Tabs>
            </Main>
        </>
    )
}
