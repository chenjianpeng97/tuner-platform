import { useEffect, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
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
    CardFooter,
    CardHeader,
    CardTitle,
} from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Textarea } from '@/components/ui/textarea'
import {
    getMySurveySubmission,
    getSurveyAssignment,
    getSurveyTemplate,
    listSurveyTemplates,
    putMySurveySubmission,
    type SurveyAssignmentDetailQM,
    type SurveyTemplateDetailQM,
    type MySurveySubmissionQM,
} from '@/api/surveys'

interface Props {
    assignmentId: string
}

export function SurveyFill({ assignmentId }: Props) {
    const navigate = useNavigate()

    const { data: assignment } = useQuery<SurveyAssignmentDetailQM>({
        queryKey: ['surveys', 'assignments', assignmentId],
        queryFn: () => getSurveyAssignment(assignmentId),
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

    const { data: existing } = useQuery<MySurveySubmissionQM>({
        queryKey: ['surveys', 'assignments', assignmentId, 'my-submission'],
        queryFn: () => getMySurveySubmission(assignmentId),
    })

    const [answers, setAnswers] = useState<Record<string, string | string[]>>({})

    useEffect(() => {
        if (existing?.answers) {
            // eslint-disable-next-line react-hooks/set-state-in-effect
            setAnswers(existing.answers as Record<string, string | string[]>)
        }
    }, [existing])

    const submitMutation = useMutation({
        mutationFn: (onlyDraft: boolean) =>
            putMySurveySubmission(assignmentId, {
                is_draft: onlyDraft,
                answers,
            }),
        onSuccess: (_, onlyDraft) => {
            if (onlyDraft) {
                toast.success('Draft saved')
            } else {
                toast.success('Survey submitted!')
                navigate({ to: '/surveys/assignments/$assignmentId', params: { assignmentId } })
            }
        },
        onError: () => toast.error('Failed to save'),
    })

    const questions = template?.questions ?? []

    const allRequiredFilled = questions
        .filter((q) => q.required)
        .every((q) => {
            const a = answers[q.key]
            if (!a) return false
            if (Array.isArray(a)) return a.length > 0
            return String(a).trim().length > 0
        })

    function setSingle(key: string, value: string) {
        setAnswers((prev) => ({ ...prev, [key]: value }))
    }

    function toggleMulti(key: string, option: string) {
        setAnswers((prev) => {
            const current = (prev[key] as string[] | undefined) ?? []
            const next = current.includes(option)
                ? current.filter((v) => v !== option)
                : [...current, option]
            return { ...prev, [key]: next }
        })
    }

    return (
        <>
            <Header>
                <div className='flex items-center gap-2 ml-auto'>
                    <ThemeSwitch />
                    <ProfileDropdown />
                </div>
            </Header>

            <Main className='flex justify-center'>
                <div className='w-full max-w-2xl space-y-6'>
                    {/* Breadcrumb */}
                    <nav className='flex items-center gap-1 text-sm text-muted-foreground'>
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
                        <span className='text-foreground font-medium'>Fill Survey</span>
                    </nav>

                    {/* Deadline banner */}
                    {assignment?.due_at && (
                        <div className='rounded-md border border-yellow-200 bg-yellow-50 px-4 py-3 text-sm text-yellow-800 dark:border-yellow-800 dark:bg-yellow-950 dark:text-yellow-200'>
                            Deadline: {new Date(assignment.due_at).toLocaleString()}
                        </div>
                    )}

                    {/* Template title */}
                    <div>
                        <h1 className='text-2xl font-bold'>{template?.name ?? 'Survey'}</h1>
                        <p className='text-muted-foreground text-sm'>
                            Please answer all required questions before submitting.
                        </p>
                    </div>

                    {/* Questions */}
                    {questions.map((q, idx) => (
                        <Card key={q.key}>
                            <CardHeader>
                                <CardTitle className='text-base'>
                                    {idx + 1}. {q.title}
                                    {q.required && <span className='ml-1 text-red-500'>*</span>}
                                </CardTitle>
                                {q.question_type !== 'text' && (
                                    <CardDescription>
                                        {q.question_type === 'multi_choice'
                                            ? 'Select all that apply'
                                            : 'Select one option'}
                                    </CardDescription>
                                )}
                            </CardHeader>
                            <CardContent>
                                {q.question_type === 'single_choice' && (
                                    <RadioGroup
                                        value={(answers[q.key] as string) ?? ''}
                                        onValueChange={(v) => setSingle(q.key, v)}
                                        className='space-y-2'
                                    >
                                        {(q.options ?? []).map((opt) => (
                                            <div key={opt} className='flex items-center gap-2'>
                                                <RadioGroupItem value={opt} id={`${q.key}-${opt}`} />
                                                <Label htmlFor={`${q.key}-${opt}`} className='cursor-pointer'>
                                                    {opt}
                                                </Label>
                                            </div>
                                        ))}
                                    </RadioGroup>
                                )}

                                {q.question_type === 'multi_choice' && (
                                    <div className='space-y-2'>
                                        {(q.options ?? []).map((opt) => {
                                            const checked = ((answers[q.key] as string[]) ?? []).includes(opt)
                                            return (
                                                <div key={opt} className='flex items-center gap-2'>
                                                    <Checkbox
                                                        id={`${q.key}-${opt}`}
                                                        checked={checked}
                                                        onCheckedChange={() => toggleMulti(q.key, opt)}
                                                    />
                                                    <Label htmlFor={`${q.key}-${opt}`} className='cursor-pointer'>
                                                        {opt}
                                                    </Label>
                                                </div>
                                            )
                                        })}
                                    </div>
                                )}

                                {q.question_type === 'text' && (
                                    <Textarea
                                        value={(answers[q.key] as string) ?? ''}
                                        onChange={(e) => setSingle(q.key, e.target.value)}
                                        placeholder='Your answer...'
                                        rows={4}
                                    />
                                )}
                            </CardContent>
                        </Card>
                    ))}

                    {/* Actions */}
                    <Card>
                        <CardFooter className='flex justify-between pt-6'>
                            <Button
                                variant='outline'
                                onClick={() => submitMutation.mutate(true)}
                                disabled={submitMutation.isPending}
                            >
                                Save Draft
                            </Button>
                            <Button
                                onClick={() => submitMutation.mutate(false)}
                                disabled={!allRequiredFilled || submitMutation.isPending}
                            >
                                Submit Survey
                            </Button>
                        </CardFooter>
                    </Card>
                </div>
            </Main>
        </>
    )
}
