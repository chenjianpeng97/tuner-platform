import { useEffect, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from '@tanstack/react-router'
import { ChevronRight, Plus, Trash2 } from 'lucide-react'
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
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import {
    getSurveyTemplate,
    publishSurveyTemplate,
    updateSurveyTemplate,
    type SurveyTemplateDetailQM,
    type UpdateSurveyTemplateRequestPydantic,
} from '@/api/surveys'

type QuestionType = 'single_choice' | 'multi_choice' | 'text'

interface QuestionDraft {
    key: string
    title: string
    question_type: QuestionType
    required: boolean
    options: string[]
}

interface Props {
    templateId: string
}

export function SurveyTemplateEdit({ templateId }: Props) {
    const queryClient = useQueryClient()

    const { data: template, isLoading } = useQuery<SurveyTemplateDetailQM>({
        queryKey: ['surveys', 'templates', templateId],
        queryFn: () => getSurveyTemplate(templateId),
    })

    const [name, setName] = useState('')
    const [questions, setQuestions] = useState<QuestionDraft[]>([])

    useEffect(() => {
        if (template) {
            // eslint-disable-next-line react-hooks/set-state-in-effect
            setName(template.name)
            setQuestions(
                (template.questions ?? []).map((q) => ({
                    key: q.key,
                    title: q.title,
                    question_type: q.question_type as QuestionType,
                    required: q.required ?? false,
                    options: q.options ?? [],
                }))
            )
        }
    }, [template])

    const saveMutation = useMutation({
        mutationFn: (payload: UpdateSurveyTemplateRequestPydantic) =>
            updateSurveyTemplate(templateId, payload),
        onSuccess: () => {
            toast.success('Template saved')
            queryClient.invalidateQueries({ queryKey: ['surveys', 'templates', templateId] })
            queryClient.invalidateQueries({ queryKey: ['surveys', 'templates'] })
        },
        onError: () => toast.error('Failed to save template'),
    })

    const publishMutation = useMutation({
        mutationFn: () => publishSurveyTemplate(templateId),
        onSuccess: () => {
            toast.success('Template published')
            queryClient.invalidateQueries({ queryKey: ['surveys', 'templates', templateId] })
            queryClient.invalidateQueries({ queryKey: ['surveys', 'templates'] })
        },
        onError: () => toast.error('Failed to publish template'),
    })

    function handleSave() {
        saveMutation.mutate({
            name,
            questions: questions.map((q) => ({
                key: q.key,
                title: q.title,
                question_type: q.question_type,
                required: q.required,
                options: q.options,
            })),
        })
    }

    function addQuestion() {
        setQuestions((prev) => [
            ...prev,
            {
                key: `q${prev.length + 1}`,
                title: '',
                question_type: 'text',
                required: false,
                options: [],
            },
        ])
    }

    function removeQuestion(index: number) {
        setQuestions((prev) => prev.filter((_, i) => i !== index))
    }

    function updateQuestion(index: number, patch: Partial<QuestionDraft>) {
        setQuestions((prev) => prev.map((q, i) => (i === index ? { ...q, ...patch } : q)))
    }

    function updateOption(qIndex: number, optIndex: number, value: string) {
        setQuestions((prev) =>
            prev.map((q, i) => {
                if (i !== qIndex) return q
                const options = [...q.options]
                options[optIndex] = value
                return { ...q, options }
            })
        )
    }

    function addOption(qIndex: number) {
        setQuestions((prev) =>
            prev.map((q, i) => (i === qIndex ? { ...q, options: [...q.options, ''] } : q))
        )
    }

    function removeOption(qIndex: number, optIndex: number) {
        setQuestions((prev) =>
            prev.map((q, i) =>
                i === qIndex ? { ...q, options: q.options.filter((_, j) => j !== optIndex) } : q
            )
        )
    }

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

    const isDraft = !template?.latest_published_version_id

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
                    <Link to='/surveys/templates' className='hover:text-foreground transition-colors'>
                        Templates
                    </Link>
                    <ChevronRight className='h-4 w-4' />
                    <span className='text-foreground font-medium'>{template?.name ?? 'Edit'}</span>
                </nav>

                <div className='mb-6 flex items-center justify-between'>
                    <div className='flex items-center gap-3'>
                        <h1 className='text-2xl font-bold'>{template?.name}</h1>
                        <Badge variant={isDraft ? 'outline' : 'default'}>
                            {isDraft ? 'Draft' : 'Published'}
                        </Badge>
                    </div>
                    <div className='flex gap-2'>
                        <Button
                            variant='outline'
                            onClick={handleSave}
                            disabled={saveMutation.isPending}
                        >
                            Save
                        </Button>
                        {isDraft && (
                            <Button
                                onClick={() => publishMutation.mutate()}
                                disabled={publishMutation.isPending}
                            >
                                Publish
                            </Button>
                        )}
                    </div>
                </div>

                <div className='space-y-6 max-w-2xl'>
                    {/* Basic info */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Template Info</CardTitle>
                            <CardDescription>Basic information for this template</CardDescription>
                        </CardHeader>
                        <CardContent className='space-y-4'>
                            <div className='space-y-2'>
                                <Label htmlFor='name'>Template Name</Label>
                                <Input
                                    id='name'
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    placeholder='Enter template name'
                                />
                            </div>
                        </CardContent>
                    </Card>

                    {/* Questions */}
                    <Card>
                        <CardHeader>
                            <div className='flex items-center justify-between'>
                                <div>
                                    <CardTitle>Questions</CardTitle>
                                    <CardDescription>Define the questions for this survey</CardDescription>
                                </div>
                                <Button variant='outline' size='sm' onClick={addQuestion}>
                                    <Plus className='mr-2 h-4 w-4' />
                                    Add Question
                                </Button>
                            </div>
                        </CardHeader>
                        <CardContent className='space-y-4'>
                            {questions.length === 0 && (
                                <p className='text-muted-foreground text-sm'>No questions yet. Add one above.</p>
                            )}
                            {questions.map((q, qIndex) => (
                                <div key={qIndex} className='rounded-lg border p-4 space-y-3'>
                                    <div className='flex items-start justify-between gap-2'>
                                        <div className='flex-1 space-y-3'>
                                            <div className='grid grid-cols-2 gap-3'>
                                                <div className='space-y-1'>
                                                    <Label>Key</Label>
                                                    <Input
                                                        value={q.key}
                                                        onChange={(e) => updateQuestion(qIndex, { key: e.target.value })}
                                                        placeholder='field_key'
                                                    />
                                                </div>
                                                <div className='space-y-1'>
                                                    <Label>Type</Label>
                                                    <Select
                                                        value={q.question_type}
                                                        onValueChange={(v) =>
                                                            updateQuestion(qIndex, { question_type: v as QuestionType })
                                                        }
                                                    >
                                                        <SelectTrigger>
                                                            <SelectValue />
                                                        </SelectTrigger>
                                                        <SelectContent>
                                                            <SelectItem value='single_choice'>Single Choice</SelectItem>
                                                            <SelectItem value='multi_choice'>Multi Choice</SelectItem>
                                                            <SelectItem value='text'>Text</SelectItem>
                                                        </SelectContent>
                                                    </Select>
                                                </div>
                                            </div>
                                            <div className='space-y-1'>
                                                <Label>Title</Label>
                                                <Input
                                                    value={q.title}
                                                    onChange={(e) => updateQuestion(qIndex, { title: e.target.value })}
                                                    placeholder='Question title shown to respondents'
                                                />
                                            </div>
                                            <div className='flex items-center gap-2'>
                                                <Switch
                                                    id={`required-${qIndex}`}
                                                    checked={q.required}
                                                    onCheckedChange={(v) => updateQuestion(qIndex, { required: v })}
                                                />
                                                <Label htmlFor={`required-${qIndex}`} className='cursor-pointer'>
                                                    Required
                                                </Label>
                                            </div>
                                            {(q.question_type === 'single_choice' ||
                                                q.question_type === 'multi_choice') && (
                                                    <div className='space-y-2'>
                                                        <Label>Options</Label>
                                                        {q.options.map((opt, optIndex) => (
                                                            <div key={optIndex} className='flex items-center gap-2'>
                                                                <Input
                                                                    value={opt}
                                                                    onChange={(e) =>
                                                                        updateOption(qIndex, optIndex, e.target.value)
                                                                    }
                                                                    placeholder={`Option ${optIndex + 1}`}
                                                                />
                                                                <Button
                                                                    variant='ghost'
                                                                    size='icon'
                                                                    onClick={() => removeOption(qIndex, optIndex)}
                                                                >
                                                                    <Trash2 className='h-4 w-4' />
                                                                </Button>
                                                            </div>
                                                        ))}
                                                        <Button
                                                            variant='outline'
                                                            size='sm'
                                                            onClick={() => addOption(qIndex)}
                                                        >
                                                            <Plus className='mr-2 h-4 w-4' />
                                                            Add Option
                                                        </Button>
                                                    </div>
                                                )}
                                        </div>
                                        <Button
                                            variant='ghost'
                                            size='icon'
                                            onClick={() => removeQuestion(qIndex)}
                                        >
                                            <Trash2 className='h-4 w-4' />
                                        </Button>
                                    </div>
                                </div>
                            ))}
                        </CardContent>
                    </Card>
                </div>
            </Main>
        </>
    )
}
