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
  type UserQueryModel,
  type UserRole,
} from '@/api/users'
import { type User } from '../data/schema'
import type { NavigateFn } from '@/hooks/use-table-url-state'

const route = getRouteApi('/_authenticated/users/')

type UsersDialogType = 'invite' | 'add' | 'edit' | 'delete'

type UsersContextType = {
  open: UsersDialogType | null
  setOpen: (str: UsersDialogType | null) => void
  currentRow: User | null
  setCurrentRow: React.Dispatch<React.SetStateAction<User | null>>
  // routing
  search: Record<string, unknown>
  navigate: NavigateFn
  // data
  users: UserQueryModel[]
  total: number
  loading: boolean
  page: number
  pageSize: number
  pageCount: number
  refreshUsers: () => Promise<void>
  // mutations
  createUser: (payload: { username: string; password: string; role: UserRole }) => void
  setPassword: (payload: { userId: string; password: string }) => void
  toggleActivation: (payload: { userId: string; isActive: boolean }) => void
  toggleAdmin: (payload: { userId: string; role: UserRole }) => void
}

const UsersContext = React.createContext<UsersContextType | null>(null)

export function UsersProvider({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useDialogState<UsersDialogType>(null)
  const [currentRow, setCurrentRow] = useState<User | null>(null)

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

  const toggleActivationMutation = useMutation({
    mutationFn: ({ userId, isActive }: { userId: string; isActive: boolean }) =>
      isActive ? deactivateUser(userId) : activateUser(userId),
    onSuccess: async () => {
      await refreshUsers()
    },
  })

  const toggleAdminMutation = useMutation({
    mutationFn: ({ userId, role }: { userId: string; role: UserRole }) =>
      role === 'admin' ? revokeAdmin(userId) : grantAdmin(userId),
    onSuccess: async () => {
      await refreshUsers()
    },
  })

  const users = (usersQuery.data?.users ?? []) as UserQueryModel[]
  const total = usersQuery.data?.total ?? 0
  const currentPage = search.page ?? 1
  const pageSize = search.pageSize ?? 10
  const pageCount = Math.max(1, Math.ceil(total / pageSize))

  const createUserFn = (payload: { username: string; password: string; role: UserRole }) =>
    createUserMutation.mutate(payload)

  const setPasswordFn = (payload: { userId: string; password: string }) =>
    setPasswordMutation.mutate(payload)

  const toggleActivationFn = (payload: { userId: string; isActive: boolean }) =>
    toggleActivationMutation.mutate(payload)

  const toggleAdminFn = (payload: { userId: string; role: UserRole }) =>
    toggleAdminMutation.mutate(payload)

  return (
    <UsersContext.Provider
      value={{
        open,
        setOpen,
        currentRow,
        setCurrentRow,
        search,
        navigate,
        users,
        total,
        loading: usersQuery.isLoading,
        page: currentPage,
        pageSize,
        pageCount,
        refreshUsers,
        createUser: createUserFn,
        setPassword: setPasswordFn,
        toggleActivation: toggleActivationFn,
        toggleAdmin: toggleAdminFn,
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
