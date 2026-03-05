import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate } from '@tanstack/react-router'
import { ChevronRight } from 'lucide-react'
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
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { createSurveyAssignment, listSurveyTemplates, type SurveyTemplateListItemQM } from '@/api/surveys'

export function SurveyAssignmentCreate() {
    const navigate = useNavigate()
    const queryClient = useQueryClient()

    const { data: templates = [] } = useQuery<SurveyTemplateListItemQM[]>({
        queryKey: ['surveys', 'templates'],
        queryFn: listSurveyTemplates,
    })

    const publishedTemplates = templates.filter((t) => t.latest_published_version_id)

    const [templateVersionId, setTemplateVersionId] = useState('')
    const [dueAt, setDueAt] = useState('')
    const [participantIds, setParticipantIds] = useState('')

    const createMutation = useMutation({
        mutationFn: () => {
            const ids = participantIds
                .split(/[\n,]+/)
                .map((s) => s.trim())
                .filter(Boolean)

            return createSurveyAssignment({
                template_version_id: templateVersionId,
                due_at: dueAt ? new Date(dueAt).toISOString() : undefined,
                assignee_user_ids: ids,
            })
        },
        onSuccess: (data) => {
            toast.success('Assignment created')
            queryClient.invalidateQueries({ queryKey: ['surveys', 'assignments'] })
            navigate({ to: '/surveys/assignments/$assignmentId', params: { assignmentId: data.id } })
        },
        onError: () => toast.error('Failed to create assignment'),
    })

    const canSubmit = Boolean(templateVersionId && participantIds.trim())

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
                    <span className='text-foreground font-medium'>New Assignment</span>
                </nav>

                <h1 className='text-2xl font-bold mb-6'>Create Assignment</h1>

                <div className='max-w-lg space-y-6'>
                    <Card>
                        <CardHeader>
                            <CardTitle>Assignment Details</CardTitle>
                            <CardDescription>Configure the survey assignment</CardDescription>
                        </CardHeader>
                        <CardContent className='space-y-4'>
                            {/* Template version */}
                            <div className='space-y-2'>
                                <Label>Template Version</Label>
                                <Select value={templateVersionId} onValueChange={setTemplateVersionId}>
                                    <SelectTrigger>
                                        <SelectValue placeholder='Select a published template...' />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {publishedTemplates.map((t) => (
                                            <SelectItem key={t.id_} value={t.latest_published_version_id!}>
                                                {t.name} — {t.latest_published_version_id!.slice(0, 8)}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                                {publishedTemplates.length === 0 && (
                                    <p className='text-xs text-muted-foreground'>
                                        No published templates.{' '}
                                        <Link
                                            to='/surveys/templates'
                                            className='underline hover:text-foreground'
                                        >
                                            Create one first.
                                        </Link>
                                    </p>
                                )}
                            </div>

                            {/* Due date */}
                            <div className='space-y-2'>
                                <Label htmlFor='due-at'>
                                    Due Date <span className='text-muted-foreground'>(optional)</span>
                                </Label>
                                <Input
                                    id='due-at'
                                    type='datetime-local'
                                    value={dueAt}
                                    onChange={(e) => setDueAt(e.target.value)}
                                />
                            </div>

                            {/* Participants */}
                            <div className='space-y-2'>
                                <Label htmlFor='participants'>Participant User IDs</Label>
                                <Textarea
                                    id='participants'
                                    value={participantIds}
                                    onChange={(e) => setParticipantIds(e.target.value)}
                                    placeholder='Enter one UUID per line or comma-separated'
                                    rows={5}
                                />
                                <p className='text-xs text-muted-foreground'>
                                    Each line or comma-separated value should be a valid user ID.
                                </p>
                            </div>
                        </CardContent>
                    </Card>

                    <div className='flex justify-end gap-3'>
                        <Button variant='outline' asChild>
                            <Link to='/surveys/assignments'>Cancel</Link>
                        </Button>
                        <Button
                            onClick={() => createMutation.mutate()}
                            disabled={!canSubmit || createMutation.isPending}
                        >
                            Create Assignment
                        </Button>
                    </div>
                </div>
            </Main>
        </>
    )
}
