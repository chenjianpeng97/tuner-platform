import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { ConfigDrawer } from '@/components/config-drawer'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { ProfileDropdown } from '@/components/profile-dropdown'
import { Search } from '@/components/search'
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import {
  closeSurveyAssignment,
  createSurveyAssignment,
  createSurveyTemplate,
  exportSurveyAuditLogsCsv,
  getMySurveySubmission,
  getSurveyAssignmentSubmissions,
  getSurveyAssignmentSummary,
  listSurveyAssignments,
  listSurveyAuditLogs,
  listSurveyTemplates,
  publishSurveyTemplate,
  putMySurveySubmission,
  updateSurveyTemplate,
} from '@/api/surveys'
import type {
  CreateSurveyAssignmentRequestPydantic,
  CreateSurveyTemplateRequestPydantic,
} from '@/api/surveys'

const queryKeys = {
  templates: ['surveys', 'templates'] as const,
  assignments: ['surveys', 'assignments'] as const,
  audits: ['surveys', 'audit-logs'] as const,
}

const defaultQuestions = JSON.stringify(
  [
    {
      key: 'role',
      title: 'Your role',
      question_type: 'single_choice',
      required: true,
      options: ['dev', 'pm', 'qa'],
    },
    {
      key: 'feedback',
      title: 'Feedback',
      question_type: 'text',
      required: false,
      options: [],
    },
  ],
  null,
  2
)

function parseJsonObject(input: string): Record<string, unknown> {
  const parsed = JSON.parse(input)
  if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
    throw new Error('Please provide a JSON object.')
  }
  return parsed as Record<string, unknown>
}

function parseQuestionPayload(input: string): CreateSurveyTemplateRequestPydantic['questions'] {
  const parsed = JSON.parse(input)
  if (!Array.isArray(parsed)) {
    throw new Error('Questions should be a JSON array.')
  }
  return parsed.map((question) => ({
    key: String(question.key ?? ''),
    title: String(question.title ?? ''),
    question_type: question.question_type,
    required: Boolean(question.required),
    options: Array.isArray(question.options)
      ? question.options.map((option: unknown) => String(option))
      : [],
  }))
}

function parseCommaIds(input: string): string[] {
  return input
    .split(',')
    .map((value) => value.trim())
    .filter(Boolean)
}

export function SurveyAssignmentWorkflow() {
  const queryClient = useQueryClient()

  const [templateName, setTemplateName] = useState('')
  const [templateQuestions, setTemplateQuestions] = useState(defaultQuestions)
  const [editTemplateId, setEditTemplateId] = useState('')

  const [assignmentTemplateVersionId, setAssignmentTemplateVersionId] = useState('')
  const [assignmentAssigneeIds, setAssignmentAssigneeIds] = useState('')
  const [assignmentDueAt, setAssignmentDueAt] = useState('')
  const [closeAssignmentId, setCloseAssignmentId] = useState('')

  const [myAssignmentId, setMyAssignmentId] = useState('')
  const [myAnswersJson, setMyAnswersJson] = useState('{\n  "role": "dev"\n}')

  const [resultAssignmentId, setResultAssignmentId] = useState('')
  const [auditFromAt, setAuditFromAt] = useState('')
  const [auditToAt, setAuditToAt] = useState('')

  const templatesQuery = useQuery({
    queryKey: queryKeys.templates,
    queryFn: () => listSurveyTemplates(),
  })

  const assignmentsQuery = useQuery({
    queryKey: queryKeys.assignments,
    queryFn: () => listSurveyAssignments(),
  })

  const auditsQuery = useQuery({
    queryKey: [...queryKeys.audits, auditFromAt, auditToAt],
    queryFn: () => listSurveyAuditLogs(auditFromAt || undefined, auditToAt || undefined),
  })

  const submissionQuery = useQuery({
    queryKey: ['surveys', 'my-submission', myAssignmentId],
    queryFn: () => getMySurveySubmission(myAssignmentId),
    enabled: Boolean(myAssignmentId),
  })

  const resultSubmissionsQuery = useQuery({
    queryKey: ['surveys', 'result-submissions', resultAssignmentId],
    queryFn: () => getSurveyAssignmentSubmissions(resultAssignmentId),
    enabled: Boolean(resultAssignmentId),
  })

  const resultSummaryQuery = useQuery({
    queryKey: ['surveys', 'result-summary', resultAssignmentId],
    queryFn: () => getSurveyAssignmentSummary(resultAssignmentId),
    enabled: Boolean(resultAssignmentId),
  })

  const createTemplateMutation = useMutation({
    mutationFn: (payload: CreateSurveyTemplateRequestPydantic) => createSurveyTemplate(payload),
    onSuccess: async () => {
      toast.success('Template created')
      await queryClient.invalidateQueries({ queryKey: queryKeys.templates })
      setTemplateName('')
    },
  })

  const updateTemplateMutation = useMutation({
    mutationFn: ({ templateId, payload }: { templateId: string; payload: CreateSurveyTemplateRequestPydantic }) =>
      updateSurveyTemplate(templateId, payload),
    onSuccess: async () => {
      toast.success('Template updated')
      await queryClient.invalidateQueries({ queryKey: queryKeys.templates })
    },
  })

  const publishTemplateMutation = useMutation({
    mutationFn: (templateId: string) => publishSurveyTemplate(templateId),
    onSuccess: async () => {
      toast.success('Template published')
      await queryClient.invalidateQueries({ queryKey: queryKeys.templates })
    },
  })

  const createAssignmentMutation = useMutation({
    mutationFn: (payload: CreateSurveyAssignmentRequestPydantic) => createSurveyAssignment(payload),
    onSuccess: async () => {
      toast.success('Assignment created')
      await queryClient.invalidateQueries({ queryKey: queryKeys.assignments })
      setAssignmentAssigneeIds('')
    },
  })

  const closeAssignmentMutation = useMutation({
    mutationFn: (assignmentId: string) => closeSurveyAssignment(assignmentId),
    onSuccess: async () => {
      toast.success('Assignment closed')
      await queryClient.invalidateQueries({ queryKey: queryKeys.assignments })
    },
  })

  const submitMyAnswersMutation = useMutation({
    mutationFn: ({ assignmentId, answers }: { assignmentId: string; answers: Record<string, unknown> }) =>
      putMySurveySubmission(assignmentId, { answers }),
    onSuccess: async (_, variables) => {
      toast.success('Submission saved')
      await queryClient.invalidateQueries({
        queryKey: ['surveys', 'my-submission', variables.assignmentId],
      })
      await queryClient.invalidateQueries({ queryKey: queryKeys.assignments })
    },
  })

  const exportAuditMutation = useMutation({
    mutationFn: () => exportSurveyAuditLogsCsv(auditFromAt || undefined, auditToAt || undefined),
    onSuccess: (csvData) => {
      navigator.clipboard.writeText(csvData).catch(() => undefined)
      toast.success('Audit CSV copied to clipboard')
    },
  })

  const templateRows = useMemo(() => templatesQuery.data ?? [], [templatesQuery.data])
  const assignmentRows = useMemo(() => assignmentsQuery.data ?? [], [assignmentsQuery.data])

  const onCreateTemplate = async () => {
    try {
      const questions = parseQuestionPayload(templateQuestions)
      await createTemplateMutation.mutateAsync({
        name: templateName.trim(),
        questions,
      })
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Invalid template payload')
    }
  }

  const onUpdateTemplate = async () => {
    if (!editTemplateId) {
      toast.error('Template ID is required for update')
      return
    }
    try {
      const questions = parseQuestionPayload(templateQuestions)
      await updateTemplateMutation.mutateAsync({
        templateId: editTemplateId,
        payload: {
          name: templateName.trim(),
          questions,
        },
      })
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Invalid template payload')
    }
  }

  const onCreateAssignment = async () => {
    try {
      await createAssignmentMutation.mutateAsync({
        template_version_id: assignmentTemplateVersionId.trim(),
        assignee_user_ids: parseCommaIds(assignmentAssigneeIds),
        due_at: assignmentDueAt || undefined,
      })
    } catch {
      toast.error('Failed to create assignment')
    }
  }

  const onSubmitMyAnswers = async () => {
    try {
      await submitMyAnswersMutation.mutateAsync({
        assignmentId: myAssignmentId,
        answers: parseJsonObject(myAnswersJson),
      })
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Invalid answer JSON')
    }
  }

  return (
    <>
      <Header fixed>
        <Search />
        <div className='ms-auto flex items-center space-x-4'>
          <ThemeSwitch />
          <ConfigDrawer />
          <ProfileDropdown />
        </div>
      </Header>

      <Main className='flex flex-1 flex-col gap-4 sm:gap-6 md:p-8 lg:p-12'>
        <div className='flex flex-wrap items-end justify-between gap-3'>
          <div>
            <h2 className='text-2xl font-bold tracking-tight'>Survey Assignment Workflow</h2>
            <p className='text-muted-foreground'>
              End-to-end workflow for template, assignment, submission, result, and audit.
            </p>
          </div>
          <Badge variant='secondary'>OpenSpec: add-survey-assignment-workflow</Badge>
        </div>

        <Tabs defaultValue='templates' className='w-full'>
          <TabsList className='grid h-auto w-full grid-cols-2 gap-2 p-1 md:grid-cols-5'>
            <TabsTrigger value='templates'>Templates</TabsTrigger>
            <TabsTrigger value='assignments'>Assignments</TabsTrigger>
            <TabsTrigger value='submission'>My Submission</TabsTrigger>
            <TabsTrigger value='results'>Results</TabsTrigger>
            <TabsTrigger value='audit'>Audit</TabsTrigger>
          </TabsList>

          <TabsContent value='templates'>
            <Card>
              <CardHeader>
                <CardTitle>Template Management</CardTitle>
                <CardDescription>Create, update, publish templates.</CardDescription>
              </CardHeader>
              <CardContent className='space-y-4'>
                <div className='grid gap-4 md:grid-cols-2'>
                  <div className='space-y-2'>
                    <Label htmlFor='template-name'>Template Name</Label>
                    <Input
                      id='template-name'
                      value={templateName}
                      onChange={(event) => setTemplateName(event.target.value)}
                      placeholder='e.g. Platform Feedback'
                    />
                  </div>
                  <div className='space-y-2'>
                    <Label htmlFor='template-id'>Edit Template ID (optional)</Label>
                    <Input
                      id='template-id'
                      value={editTemplateId}
                      onChange={(event) => setEditTemplateId(event.target.value)}
                      placeholder='template UUID for update/publish'
                    />
                  </div>
                </div>
                <div className='space-y-2'>
                  <Label htmlFor='template-questions'>Questions JSON</Label>
                  <Textarea
                    id='template-questions'
                    className='min-h-56 font-mono text-xs'
                    value={templateQuestions}
                    onChange={(event) => setTemplateQuestions(event.target.value)}
                  />
                </div>
                <div className='flex flex-wrap gap-2'>
                  <Button onClick={() => void onCreateTemplate()}>Create</Button>
                  <Button variant='secondary' onClick={() => void onUpdateTemplate()}>
                    Update
                  </Button>
                  <Button
                    variant='outline'
                    disabled={!editTemplateId}
                    onClick={() => void publishTemplateMutation.mutateAsync(editTemplateId)}
                  >
                    Publish
                  </Button>
                </div>
                <div className='rounded-md border p-3 text-sm'>
                  <p className='mb-2 font-medium'>Templates</p>
                  <ul className='space-y-1 text-muted-foreground'>
                    {templateRows.map((template) => (
                      <li key={template.id_}>
                        {template.name} · {template.id_} · latest version:{' '}
                        {template.latest_published_version_id ?? 'none'}
                      </li>
                    ))}
                  </ul>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value='assignments'>
            <Card>
              <CardHeader>
                <CardTitle>Assignment Management</CardTitle>
                <CardDescription>Create and close assignment tasks.</CardDescription>
              </CardHeader>
              <CardContent className='space-y-4'>
                <div className='grid gap-4 md:grid-cols-3'>
                  <div className='space-y-2'>
                    <Label htmlFor='template-version-id'>Template Version ID</Label>
                    <Input
                      id='template-version-id'
                      value={assignmentTemplateVersionId}
                      onChange={(event) => setAssignmentTemplateVersionId(event.target.value)}
                    />
                  </div>
                  <div className='space-y-2'>
                    <Label htmlFor='assignee-ids'>Assignee IDs (comma separated)</Label>
                    <Input
                      id='assignee-ids'
                      value={assignmentAssigneeIds}
                      onChange={(event) => setAssignmentAssigneeIds(event.target.value)}
                    />
                  </div>
                  <div className='space-y-2'>
                    <Label htmlFor='due-at'>Due At (optional ISO)</Label>
                    <Input
                      id='due-at'
                      value={assignmentDueAt}
                      onChange={(event) => setAssignmentDueAt(event.target.value)}
                      placeholder='2026-03-05T10:00:00+00:00'
                    />
                  </div>
                </div>
                <div className='flex flex-wrap gap-2'>
                  <Button onClick={() => void onCreateAssignment()}>Create Assignment</Button>
                </div>

                <div className='grid gap-4 md:grid-cols-2'>
                  <div className='rounded-md border p-3 text-sm'>
                    <p className='mb-2 font-medium'>Assignments</p>
                    <ul className='space-y-1 text-muted-foreground'>
                      {assignmentRows.map((assignment) => (
                        <li key={assignment.id_}>
                          {assignment.id_} · {assignment.status} · {assignment.submitted_count}/
                          {assignment.assignee_count}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className='space-y-2 rounded-md border p-3'>
                    <Label htmlFor='close-assignment-id'>Close Assignment ID</Label>
                    <Input
                      id='close-assignment-id'
                      value={closeAssignmentId}
                      onChange={(event) => setCloseAssignmentId(event.target.value)}
                    />
                    <Button
                      variant='outline'
                      disabled={!closeAssignmentId}
                      onClick={() =>
                        void closeAssignmentMutation.mutateAsync(closeAssignmentId)
                      }
                    >
                      Close Assignment
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value='submission'>
            <Card>
              <CardHeader>
                <CardTitle>My Submission</CardTitle>
                <CardDescription>Load and overwrite your own submission snapshot.</CardDescription>
              </CardHeader>
              <CardContent className='space-y-4'>
                <div className='space-y-2'>
                  <Label htmlFor='my-assignment-id'>Assignment ID</Label>
                  <Input
                    id='my-assignment-id'
                    value={myAssignmentId}
                    onChange={(event) => setMyAssignmentId(event.target.value)}
                  />
                </div>
                <div className='flex gap-2'>
                  <Button
                    variant='secondary'
                    disabled={!myAssignmentId}
                    onClick={() => void submissionQuery.refetch()}
                  >
                    Load My Submission
                  </Button>
                </div>
                <div className='space-y-2'>
                  <Label htmlFor='my-answers-json'>Answers JSON</Label>
                  <Textarea
                    id='my-answers-json'
                    className='min-h-44 font-mono text-xs'
                    value={myAnswersJson}
                    onChange={(event) => setMyAnswersJson(event.target.value)}
                  />
                </div>
                <Button
                  disabled={!myAssignmentId}
                  onClick={() => void onSubmitMyAnswers()}
                >
                  Save My Submission
                </Button>
                <div className='rounded-md border p-3 text-xs text-muted-foreground'>
                  <p className='mb-2 font-medium text-foreground'>Current Snapshot</p>
                  <pre>{JSON.stringify(submissionQuery.data ?? null, null, 2)}</pre>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value='results'>
            <Card>
              <CardHeader>
                <CardTitle>Results</CardTitle>
                <CardDescription>Inspect detailed submissions and aggregated summary.</CardDescription>
              </CardHeader>
              <CardContent className='space-y-4'>
                <div className='space-y-2'>
                  <Label htmlFor='result-assignment-id'>Assignment ID</Label>
                  <Input
                    id='result-assignment-id'
                    value={resultAssignmentId}
                    onChange={(event) => setResultAssignmentId(event.target.value)}
                  />
                </div>
                <div className='flex gap-2'>
                  <Button
                    variant='secondary'
                    disabled={!resultAssignmentId}
                    onClick={() => {
                      void resultSubmissionsQuery.refetch()
                      void resultSummaryQuery.refetch()
                    }}
                  >
                    Load Results
                  </Button>
                </div>
                <div className='grid gap-4 md:grid-cols-2'>
                  <div className='rounded-md border p-3 text-xs text-muted-foreground'>
                    <p className='mb-2 font-medium text-foreground'>Submissions</p>
                    <pre>{JSON.stringify(resultSubmissionsQuery.data ?? [], null, 2)}</pre>
                  </div>
                  <div className='rounded-md border p-3 text-xs text-muted-foreground'>
                    <p className='mb-2 font-medium text-foreground'>Summary</p>
                    <pre>{JSON.stringify(resultSummaryQuery.data ?? null, null, 2)}</pre>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value='audit'>
            <Card>
              <CardHeader>
                <CardTitle>Audit Logs</CardTitle>
                <CardDescription>
                  Query and export raw-response access audit records.
                </CardDescription>
              </CardHeader>
              <CardContent className='space-y-4'>
                <div className='grid gap-4 md:grid-cols-2'>
                  <div className='space-y-2'>
                    <Label htmlFor='audit-from'>From (optional ISO)</Label>
                    <Input
                      id='audit-from'
                      value={auditFromAt}
                      onChange={(event) => setAuditFromAt(event.target.value)}
                    />
                  </div>
                  <div className='space-y-2'>
                    <Label htmlFor='audit-to'>To (optional ISO)</Label>
                    <Input
                      id='audit-to'
                      value={auditToAt}
                      onChange={(event) => setAuditToAt(event.target.value)}
                    />
                  </div>
                </div>
                <div className='flex flex-wrap gap-2'>
                  <Button
                    variant='secondary'
                    onClick={() => void auditsQuery.refetch()}
                  >
                    Refresh Logs
                  </Button>
                  <Button
                    variant='outline'
                    onClick={() => void exportAuditMutation.mutateAsync()}
                  >
                    Export CSV (copy)
                  </Button>
                </div>
                <div className='rounded-md border p-3 text-xs text-muted-foreground'>
                  <pre>{JSON.stringify(auditsQuery.data ?? [], null, 2)}</pre>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </Main>
    </>
  )
}
