import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from '@tanstack/react-router'
import { Plus } from 'lucide-react'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { ProfileDropdown } from '@/components/profile-dropdown'
import { ThemeSwitch } from '@/components/theme-switch'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
    Card,
    CardContent,
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
import { listSurveyAssignments, type SurveyAssignmentListItemQM } from '@/api/surveys'

function formatDate(value: string | null | undefined): string {
    if (!value) return '—'
    return new Date(value).toLocaleDateString()
}

export function SurveyAssignmentList() {
    const { data: assignments = [], isLoading } = useQuery<SurveyAssignmentListItemQM[]>({
        queryKey: ['surveys', 'assignments'],
        queryFn: listSurveyAssignments,
    })

    const stats = useMemo(() => {
        const total = assignments.length
        const inProgress = assignments.filter((a) => a.status === 'in_progress').length
        const completed = assignments.filter((a) => a.status === 'completed').length
        return { total, inProgress, completed }
    }, [assignments])

    return (
        <>
            <Header>
                <div className='flex items-center gap-2 ml-auto'>
                    <ThemeSwitch />
                    <ProfileDropdown />
                </div>
            </Header>

            <Main>
                <div className='mb-6 flex items-center justify-between'>
                    <div>
                        <h1 className='text-2xl font-bold'>Survey Assignments</h1>
                        <p className='text-muted-foreground text-sm'>Track and manage survey assignments</p>
                    </div>
                    <Button asChild>
                        <Link to='/surveys/assignments/new'>
                            <Plus className='mr-2 h-4 w-4' />
                            New Assignment
                        </Link>
                    </Button>
                </div>

                {/* Stat cards */}
                <div className='mb-6 grid gap-4 md:grid-cols-3'>
                    <Card>
                        <CardHeader className='pb-2'>
                            <CardTitle className='text-sm font-medium text-muted-foreground'>
                                Total
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className='text-3xl font-bold'>{stats.total}</p>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader className='pb-2'>
                            <CardTitle className='text-sm font-medium text-muted-foreground'>
                                In Progress
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className='text-3xl font-bold text-blue-600'>{stats.inProgress}</p>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader className='pb-2'>
                            <CardTitle className='text-sm font-medium text-muted-foreground'>
                                Completed
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className='text-3xl font-bold text-green-600'>{stats.completed}</p>
                        </CardContent>
                    </Card>
                </div>

                {/* Table */}
                {isLoading ? (
                    <p className='text-muted-foreground text-sm'>Loading...</p>
                ) : assignments.length === 0 ? (
                    <p className='text-muted-foreground text-sm'>No assignments yet.</p>
                ) : (
                    <div className='rounded-md border'>
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>ID</TableHead>
                                    <TableHead>Status</TableHead>
                                    <TableHead>Progress</TableHead>
                                    <TableHead>Due Date</TableHead>
                                    <TableHead />
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {assignments.map((a) => {
                                    const pct = Math.round((a.ratio ?? 0) * 100)
                                    return (
                                        <TableRow key={a.id_}>
                                            <TableCell className='font-mono text-xs'>
                                                {a.id_.slice(0, 8)}
                                            </TableCell>
                                            <TableCell>
                                                <Badge
                                                    variant={a.status === 'completed' ? 'default' : 'secondary'}
                                                >
                                                    {a.status === 'in_progress' ? 'In Progress' : 'Completed'}
                                                </Badge>
                                            </TableCell>
                                            <TableCell>
                                                <div className='flex items-center gap-2 min-w-[140px]'>
                                                    <Progress value={pct} className='h-2 flex-1' />
                                                    <span className='text-xs text-muted-foreground whitespace-nowrap'>
                                                        {a.submitted_count}/{a.assignee_count} ({pct}%)
                                                    </span>
                                                </div>
                                            </TableCell>
                                            <TableCell className='text-sm text-muted-foreground'>
                                                {formatDate(a.due_at)}
                                            </TableCell>
                                            <TableCell className='text-right'>
                                                <Button variant='outline' size='sm' asChild>
                                                    <Link
                                                        to='/surveys/assignments/$assignmentId'
                                                        params={{ assignmentId: a.id_ }}
                                                    >
                                                        Details
                                                    </Link>
                                                </Button>
                                            </TableCell>
                                        </TableRow>
                                    )
                                })}
                            </TableBody>
                        </Table>
                    </div>
                )}
            </Main>
        </>
    )
}
