import React, { useMemo, useState } from 'react'
import useDialogState from '@/hooks/use-dialog-state'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getRouteApi } from '@tanstack/react-router'
import {
  activateUser,
  createUser,
  deactivateUser,
  grantAdmin,
  listUsers,
  revokeAdmin,
  setUserPassword,
  type UserRole,
} from '@/api/users'
import type { NavigateFn } from '@/hooks/use-table-url-state'
import { type UsersRowViewModel, toUsersRows } from '../model'

const route = getRouteApi('/_authenticated/users/')

type UsersDialogType = 'add' | 'edit'

type UsersContextType = {
  open: UsersDialogType | null
  setOpen: (str: UsersDialogType | null) => void
  currentRow: UsersRowViewModel | null
  setCurrentRow: React.Dispatch<React.SetStateAction<UsersRowViewModel | null>>
  // routing
  search: Record<string, unknown>
  navigate: NavigateFn
  // data
  rows: UsersRowViewModel[]
  total: number
  loading: boolean
  page: number
  pageSize: number
  pageCount: number
  refreshUsers: () => Promise<void>
  // mutations
  createUser: (payload: {
    username: string
    password: string
    role: UserRole
  }) => Promise<void>
  setPassword: (payload: { userId: string; password: string }) => Promise<void>
  setUserActivation: (payload: {
    userId: string
    isActive: boolean
  }) => Promise<void>
  setUserAdmin: (payload: { userId: string; isAdmin: boolean }) => Promise<void>
}

const UsersContext = React.createContext<UsersContextType | null>(null)

export function UsersProvider({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useDialogState<UsersDialogType>(null)
  const [currentRow, setCurrentRow] = useState<UsersRowViewModel | null>(null)

  const search = route.useSearch()
  const routeNavigate = route.useNavigate()
  const navigate = routeNavigate as unknown as NavigateFn
  const queryClient = useQueryClient()

  const queryInput = useMemo(
    () => ({
      page: search.page ?? 1,
      pageSize: search.pageSize ?? 10,
      sortingField: search.sortingField ?? 'username',
      sortingOrder: search.sortingOrder ?? 'ASC',
    }),
    [search.page, search.pageSize, search.sortingField, search.sortingOrder]
  )

  const usersQuery = useQuery({
    queryKey: ['users', queryInput],
    queryFn: () => listUsers(queryInput),
  })

  const refreshUsers = async () => {
    await queryClient.invalidateQueries({ queryKey: ['users'] })
  }

  const createUserMutation = useMutation({
    mutationFn: createUser,
    onSuccess: async () => {
      await refreshUsers()
    },
  })

  const setPasswordMutation = useMutation({
    mutationFn: ({ userId, password }: { userId: string; password: string }) =>
      setUserPassword(userId, password),
    onSuccess: () => {
      // no-op
    },
  })

  const setActivationMutation = useMutation({
    mutationFn: ({ userId, isActive }: { userId: string; isActive: boolean }) =>
      isActive ? activateUser(userId) : deactivateUser(userId),
    onSuccess: async () => {
      await refreshUsers()
    },
  })

  const setAdminMutation = useMutation({
    mutationFn: ({ userId, isAdmin }: { userId: string; isAdmin: boolean }) =>
      isAdmin ? grantAdmin(userId) : revokeAdmin(userId),
    onSuccess: async () => {
      await refreshUsers()
    },
  })

  const rows = toUsersRows(usersQuery.data?.users ?? [])
  const total = usersQuery.data?.total ?? 0
  const currentPage = search.page ?? 1
  const pageSize = search.pageSize ?? 10
  const pageCount = Math.max(1, Math.ceil(total / pageSize))

  const createUserFn = async (payload: {
    username: string
    password: string
    role: UserRole
  }) => {
    await createUserMutation.mutateAsync(payload)
  }

  const setPasswordFn = async (payload: { userId: string; password: string }) => {
    await setPasswordMutation.mutateAsync(payload)
  }

  const setUserActivationFn = async (payload: {
    userId: string
    isActive: boolean
  }) => {
    await setActivationMutation.mutateAsync(payload)
  }

  const setUserAdminFn = async (payload: {
    userId: string
    isAdmin: boolean
  }) => {
    await setAdminMutation.mutateAsync(payload)
  }

  return (
    <UsersContext.Provider
      value={{
        open,
        setOpen,
        currentRow,
        setCurrentRow,
        search,
        navigate,
        rows,
        total,
        loading: usersQuery.isLoading,
        page: currentPage,
        pageSize,
        pageCount,
        refreshUsers,
        createUser: createUserFn,
        setPassword: setPasswordFn,
        setUserActivation: setUserActivationFn,
        setUserAdmin: setUserAdminFn,
      }}
    >
      {children}
    </UsersContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export const useUsers = () => {
  const usersContext = React.useContext(UsersContext)

  if (!usersContext) {
    throw new Error('useUsers has to be used within <UsersContext>')
  }

  return usersContext
}
