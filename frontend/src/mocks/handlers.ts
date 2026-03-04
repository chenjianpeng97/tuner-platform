import { http, HttpResponse } from 'msw'
import accountFixture from '@/mocks/fixtures/account.json'
import errorFixture from '@/mocks/fixtures/errors.json'
import surveysFixture from '@/mocks/fixtures/surveys.json'
import usersFixture from '@/mocks/fixtures/users.json'

const usersState = [...usersFixture.users]
const templatesState: any[] = [...surveysFixture.templates]
const templateDetailsState: Record<string, any> = { ...surveysFixture.templateDetails }
const assignmentsState: any[] = [...surveysFixture.assignments]
const assignmentDetailsState: Record<string, any> = { ...surveysFixture.assignmentDetails }
const mySubmissionsState: Record<string, any> = { ...surveysFixture.mySubmissions }
const submissionsState: Record<string, any[]> = { ...surveysFixture.submissions }
const summariesState: Record<string, any> = { ...surveysFixture.summaries }
const auditLogsState: any[] = [...surveysFixture.auditLogs]

const API_BASE = '*/api/v1'

export const handlers = [
  http.post(`${API_BASE}/account/signup`, () =>
    HttpResponse.json(accountFixture.defaultSignupResponse, { status: 201 })
  ),
  http.post(`${API_BASE}/account/login`, () => new HttpResponse(null, { status: 204 })),
  http.delete(`${API_BASE}/account/logout`, () => new HttpResponse(null, { status: 204 })),
  http.put(`${API_BASE}/account/password`, () => new HttpResponse(null, { status: 204 })),

  http.get(`${API_BASE}/users/`, ({ request }) => {
    const url = new URL(request.url)
    const limit = Number(url.searchParams.get('limit') ?? 20)
    const offset = Number(url.searchParams.get('offset') ?? 0)
    const sortingField = url.searchParams.get('sorting_field') ?? 'username'
    const sortingOrder = url.searchParams.get('sorting_order') ?? 'ASC'

    const sortedUsers = [...usersState].sort((a, b) => {
      const left = String(a[sortingField as keyof typeof a] ?? '')
      const right = String(b[sortingField as keyof typeof b] ?? '')
      if (left === right) return 0
      const result = left > right ? 1 : -1
      return sortingOrder === 'DESC' ? -result : result
    })

    return HttpResponse.json(
      {
        users: sortedUsers.slice(offset, offset + limit),
        total: usersState.length,
      },
      { status: 200 }
    )
  }),

  http.post(`${API_BASE}/users/`, async ({ request }) => {
    const payload = (await request.json()) as {
      username: string
      role?: 'super_admin' | 'admin' | 'user'
    }

    if (usersState.some((u) => u.username === payload.username)) {
      return HttpResponse.json(errorFixture.conflict, { status: 409 })
    }

    const id = crypto.randomUUID()
    usersState.push({
      id_: id,
      username: payload.username,
      role: payload.role ?? 'user',
      is_active: true,
    })

    return HttpResponse.json({ id }, { status: 201 })
  }),

  http.put(`${API_BASE}/users/:userId/password`, ({ params }) => {
    const found = usersState.find((u) => u.id_ === params.userId)
    if (!found) return HttpResponse.json(errorFixture.notFound, { status: 404 })
    return new HttpResponse(null, { status: 204 })
  }),

  http.put(`${API_BASE}/users/:userId/roles/admin`, ({ params }) => {
    const found = usersState.find((u) => u.id_ === params.userId)
    if (!found) return HttpResponse.json(errorFixture.notFound, { status: 404 })
    if (found.role === 'super_admin') {
      return HttpResponse.json(errorFixture.forbidden, { status: 403 })
    }
    found.role = 'admin'
    return new HttpResponse(null, { status: 204 })
  }),

  http.delete(`${API_BASE}/users/:userId/roles/admin`, ({ params }) => {
    const found = usersState.find((u) => u.id_ === params.userId)
    if (!found) return HttpResponse.json(errorFixture.notFound, { status: 404 })
    if (found.role === 'super_admin') {
      return HttpResponse.json(errorFixture.forbidden, { status: 403 })
    }
    found.role = 'user'
    return new HttpResponse(null, { status: 204 })
  }),

  http.put(`${API_BASE}/users/:userId/activation`, ({ params }) => {
    const found = usersState.find((u) => u.id_ === params.userId)
    if (!found) return HttpResponse.json(errorFixture.notFound, { status: 404 })
    found.is_active = true
    return new HttpResponse(null, { status: 204 })
  }),

  http.delete(`${API_BASE}/users/:userId/activation`, ({ params }) => {
    const found = usersState.find((u) => u.id_ === params.userId)
    if (!found) return HttpResponse.json(errorFixture.notFound, { status: 404 })
    if (found.role === 'super_admin') {
      return HttpResponse.json(errorFixture.forbidden, { status: 403 })
    }
    found.is_active = false
    return new HttpResponse(null, { status: 204 })
  }),

  http.get(`${API_BASE}/surveys/templates`, () =>
    HttpResponse.json(templatesState, { status: 200 })
  ),

  http.post(`${API_BASE}/surveys/templates`, async ({ request }) => {
    const payload = (await request.json()) as {
      name: string
      questions: Array<{
        key: string
        title: string
        question_type: string
        required: boolean
        options: string[]
      }>
    }
    const id = crypto.randomUUID()
    templatesState.unshift({ id_: id, name: payload.name, latest_published_version_id: null })
    templateDetailsState[id] = {
      id_: id,
      name: payload.name,
      latest_published_version_id: null,
      questions: payload.questions,
    }
    return HttpResponse.json({ id }, { status: 201 })
  }),

  http.get(`${API_BASE}/surveys/templates/:templateId`, ({ params }) => {
    const templateId = String(params.templateId ?? '')
    const data = templateDetailsState[templateId]
    if (!data) return HttpResponse.json(errorFixture.notFound, { status: 404 })
    return HttpResponse.json(data, { status: 200 })
  }),

  http.patch(`${API_BASE}/surveys/templates/:templateId`, async ({ params, request }) => {
    const templateId = String(params.templateId ?? '')
    const data = templateDetailsState[templateId]
    if (!data) return HttpResponse.json(errorFixture.notFound, { status: 404 })
    const payload = (await request.json()) as {
      name: string
      questions: Array<{
        key: string
        title: string
        question_type: string
        required: boolean
        options: string[]
      }>
    }
    data.name = payload.name
    data.questions = payload.questions
    const idx = templatesState.findIndex((t) => t.id_ === templateId)
    if (idx >= 0) templatesState[idx].name = payload.name
    return new HttpResponse(null, { status: 204 })
  }),

  http.post(`${API_BASE}/surveys/templates/:templateId/publish`, ({ params }) => {
    const templateId = String(params.templateId ?? '')
    const data = templateDetailsState[templateId]
    if (!data) return HttpResponse.json(errorFixture.notFound, { status: 404 })
    const versionId = crypto.randomUUID()
    data.latest_published_version_id = versionId
    const idx = templatesState.findIndex((t) => t.id_ === templateId)
    if (idx >= 0) templatesState[idx].latest_published_version_id = versionId
    return HttpResponse.json({ version_id: versionId }, { status: 201 })
  }),

  http.get(`${API_BASE}/surveys/assignments`, () =>
    HttpResponse.json(assignmentsState, { status: 200 })
  ),

  http.post(`${API_BASE}/surveys/assignments`, async ({ request }) => {
    const payload = (await request.json()) as {
      template_version_id: string
      assignee_user_ids: string[]
      due_at?: string | null
    }
    const id = crypto.randomUUID()
    const item = {
      id_: id,
      template_version_id: payload.template_version_id,
      status: 'in_progress' as const,
      due_at: payload.due_at ?? null,
      assignee_count: payload.assignee_user_ids.length,
      submitted_count: 0,
      ratio: 0,
    }
    assignmentsState.unshift(item)
    assignmentDetailsState[id] = {
      ...item,
      assignee_user_ids: payload.assignee_user_ids,
    }
    return HttpResponse.json({ id }, { status: 201 })
  }),

  http.get(`${API_BASE}/surveys/assignments/:assignmentId`, ({ params }) => {
    const assignmentId = String(params.assignmentId ?? '')
    const data = assignmentDetailsState[assignmentId]
    if (!data) return HttpResponse.json(errorFixture.notFound, { status: 404 })
    return HttpResponse.json(data, { status: 200 })
  }),

  http.post(`${API_BASE}/surveys/assignments/:assignmentId/close`, ({ params }) => {
    const assignmentId = String(params.assignmentId ?? '')
    const detail = assignmentDetailsState[assignmentId]
    if (!detail) return HttpResponse.json(errorFixture.notFound, { status: 404 })
    detail.status = 'completed'
    const idx = assignmentsState.findIndex((a) => a.id_ === assignmentId)
    if (idx >= 0) assignmentsState[idx].status = 'completed'
    return new HttpResponse(null, { status: 204 })
  }),

  http.get(`${API_BASE}/surveys/assignments/:assignmentId/my-submission`, ({ params }) => {
    const assignmentId = String(params.assignmentId ?? '')
    const data = mySubmissionsState[assignmentId]
    if (!data) {
      return HttpResponse.json(
        {
          assignment_id: assignmentId,
          assignee_user_id: usersState[0]?.id_ ?? crypto.randomUUID(),
          answers: {},
          submitted_at: null,
        },
        { status: 200 }
      )
    }
    return HttpResponse.json(data, { status: 200 })
  }),

  http.put(`${API_BASE}/surveys/assignments/:assignmentId/my-submission`, async ({ params, request }) => {
    const payload = (await request.json()) as { answers: Record<string, unknown> }
    const assignmentId = String(params.assignmentId ?? '')
    mySubmissionsState[assignmentId] = {
      assignment_id: assignmentId,
      assignee_user_id: usersState[0]?.id_ ?? crypto.randomUUID(),
      answers: payload.answers,
      submitted_at: new Date().toISOString(),
    }
    return new HttpResponse(null, { status: 204 })
  }),

  http.get(`${API_BASE}/surveys/assignments/:assignmentId/submissions`, ({ params }) => {
    const assignmentId = String(params.assignmentId ?? '')
    const data = submissionsState[assignmentId] ?? []
    return HttpResponse.json(data, { status: 200 })
  }),

  http.get(`${API_BASE}/surveys/assignments/:assignmentId/summary`, ({ params }) => {
    const assignmentId = String(params.assignmentId ?? '')
    const data = summariesState[assignmentId]
    if (!data) return HttpResponse.json(errorFixture.notFound, { status: 404 })
    return HttpResponse.json(data, { status: 200 })
  }),

  http.get(`${API_BASE}/surveys/audit-logs`, () =>
    HttpResponse.json(auditLogsState, { status: 200 })
  ),

  http.get(`${API_BASE}/surveys/audit-logs/export`, () => {
    const lines = [
      'id,actor_user_id,assignment_id,action,occurred_at',
      ...auditLogsState.map(
        (row) =>
          `${row.id_},${row.actor_user_id},${row.assignment_id},${row.action},${row.occurred_at}`
      ),
    ]
    return new HttpResponse(lines.join('\n'), {
      status: 200,
      headers: {
        'Content-Type': 'text/csv',
      },
    })
  }),
]
