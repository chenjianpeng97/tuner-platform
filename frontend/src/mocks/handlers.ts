import { http, HttpResponse } from 'msw'
import accountFixture from '@/mocks/fixtures/account.json'
import usersFixture from '@/mocks/fixtures/users.json'
import errorFixture from '@/mocks/fixtures/errors.json'

const usersState = [...usersFixture.users]
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

    const pagedUsers = sortedUsers.slice(offset, offset + limit)

    return HttpResponse.json(
      {
        users: pagedUsers,
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
]
