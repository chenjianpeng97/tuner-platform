import { useMemo, useState } from 'react'
import { getRouteApi } from '@tanstack/react-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { ConfigDrawer } from '@/components/config-drawer'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { ProfileDropdown } from '@/components/profile-dropdown'
import { Search } from '@/components/search'
import { ThemeSwitch } from '@/components/theme-switch'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import {
  activateUser,
  canToggleAdmin,
  createUser,
  deactivateUser,
  grantAdmin,
  isAdminRole,
  listUsers,
  revokeAdmin,
  setUserPassword,
  toRoleLabel,
  toStatusLabel,
  type UserRole,
} from '@/api/users'

const route = getRouteApi('/_authenticated/users/')

const PAGE_SIZE_OPTIONS = [10, 20, 50]

export function Users() {
  const search = route.useSearch()
  const navigate = route.useNavigate()
  const queryClient = useQueryClient()

  const [newUsername, setNewUsername] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [newRole, setNewRole] = useState<UserRole>('user')

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
      toast.success('User created')
      setNewUsername('')
      setNewPassword('')
      setNewRole('user')
      await refreshUsers()
    },
  })

  const setPasswordMutation = useMutation({
    mutationFn: ({ userId, password }: { userId: string; password: string }) =>
      setUserPassword(userId, password),
    onSuccess: () => toast.success('Password updated'),
  })

  const toggleActivationMutation = useMutation({
    mutationFn: ({ userId, isActive }: { userId: string; isActive: boolean }) =>
      isActive ? deactivateUser(userId) : activateUser(userId),
    onSuccess: async () => {
      toast.success('User status updated')
      await refreshUsers()
    },
  })

  const toggleAdminMutation = useMutation({
    mutationFn: ({ userId, role }: { userId: string; role: UserRole }) =>
      role === 'admin' ? revokeAdmin(userId) : grantAdmin(userId),
    onSuccess: async () => {
      toast.success('User role updated')
      await refreshUsers()
    },
  })

  const users = usersQuery.data?.users ?? []
  const total = usersQuery.data?.total ?? 0
  const currentPage = search.page ?? 1
  const pageSize = search.pageSize ?? 10
  const pageCount = Math.max(1, Math.ceil(total / pageSize))

  const onCreateUser = () => {
    if (!newUsername.trim() || !newPassword.trim()) {
      toast.error('Username and password are required')
      return
    }

    createUserMutation.mutate({
      username: newUsername.trim(),
      password: newPassword,
      role: newRole,
    })
  }

  const onChangePassword = (userId: string) => {
    const password = window.prompt('Enter new password')
    if (!password) return

    setPasswordMutation.mutate({ userId, password })
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

      <Main className='flex flex-1 flex-col gap-4 sm:gap-6'>
        <div className='flex flex-wrap items-end justify-between gap-2'>
          <div>
            <h2 className='text-2xl font-bold tracking-tight'>User List</h2>
            <p className='text-muted-foreground'>
              Contract-driven users management (current iteration scope: pagination + sorting).
            </p>
          </div>
        </div>

        <div className='grid gap-4 rounded-md border p-4 md:grid-cols-4'>
          <div className='space-y-2'>
            <Label htmlFor='new-username'>Username</Label>
            <Input
              id='new-username'
              value={newUsername}
              onChange={(event) => setNewUsername(event.target.value)}
              placeholder='new_user'
            />
          </div>
          <div className='space-y-2'>
            <Label htmlFor='new-password'>Password</Label>
            <Input
              id='new-password'
              type='password'
              value={newPassword}
              onChange={(event) => setNewPassword(event.target.value)}
              placeholder='******'
            />
          </div>
          <div className='space-y-2'>
            <Label htmlFor='new-role'>Role</Label>
            <Select value={newRole} onValueChange={(value) => setNewRole(value as UserRole)}>
              <SelectTrigger id='new-role'>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value='user'>User</SelectItem>
                <SelectItem value='admin'>Admin</SelectItem>
                <SelectItem value='super_admin'>Super Admin</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className='flex items-end'>
            <Button className='w-full' onClick={onCreateUser} disabled={createUserMutation.isPending}>
              Create User
            </Button>
          </div>
        </div>

        <div className='flex flex-wrap items-center justify-between gap-3 rounded-md border p-4'>
          <div className='flex items-center gap-2'>
            <Label htmlFor='sort-field'>Sorting field</Label>
            <Select
              value={search.sortingField ?? 'username'}
              onValueChange={(value) =>
                navigate({
                  search: (prev) => ({ ...prev, page: 1, sortingField: value }),
                })
              }
            >
              <SelectTrigger id='sort-field' className='w-[180px]'>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value='username'>username</SelectItem>
                <SelectItem value='role'>role</SelectItem>
                <SelectItem value='is_active'>is_active</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className='flex items-center gap-2'>
            <Label htmlFor='sort-order'>Sorting order</Label>
            <Select
              value={search.sortingOrder ?? 'ASC'}
              onValueChange={(value) =>
                navigate({
                  search: (prev) => ({ ...prev, page: 1, sortingOrder: value as 'ASC' | 'DESC' }),
                })
              }
            >
              <SelectTrigger id='sort-order' className='w-[120px]'>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value='ASC'>ASC</SelectItem>
                <SelectItem value='DESC'>DESC</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className='flex items-center gap-2'>
            <Label htmlFor='page-size'>Page size</Label>
            <Select
              value={String(pageSize)}
              onValueChange={(value) =>
                navigate({
                  search: (prev) => ({ ...prev, page: 1, pageSize: Number(value) }),
                })
              }
            >
              <SelectTrigger id='page-size' className='w-[100px]'>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {PAGE_SIZE_OPTIONS.map((option) => (
                  <SelectItem key={option} value={String(option)}>
                    {option}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className='overflow-hidden rounded-md border'>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Username</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className='text-right'>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {usersQuery.isLoading && (
                <TableRow>
                  <TableCell colSpan={4}>Loading...</TableCell>
                </TableRow>
              )}

              {!usersQuery.isLoading && users.length === 0 && (
                <TableRow>
                  <TableCell colSpan={4}>No users found</TableCell>
                </TableRow>
              )}

              {!usersQuery.isLoading &&
                users.map((user) => (
                  <TableRow key={user.id_}>
                    <TableCell>{user.username}</TableCell>
                    <TableCell>{toRoleLabel(user.role)}</TableCell>
                    <TableCell>{toStatusLabel(user)}</TableCell>
                    <TableCell className='space-x-2 text-right'>
                      <Button variant='outline' size='sm' onClick={() => onChangePassword(user.id_)}>
                        Set Password
                      </Button>
                      <Button
                        variant='outline'
                        size='sm'
                        disabled={!canToggleAdmin(user.role) || toggleAdminMutation.isPending}
                        onClick={() =>
                          toggleAdminMutation.mutate({
                            userId: user.id_,
                            role: user.role,
                          })
                        }
                      >
                        {isAdminRole(user.role) ? 'Revoke Admin' : 'Grant Admin'}
                      </Button>
                      <Button
                        variant='outline'
                        size='sm'
                        disabled={toggleActivationMutation.isPending}
                        onClick={() =>
                          toggleActivationMutation.mutate({
                            userId: user.id_,
                            isActive: user.is_active,
                          })
                        }
                      >
                        {user.is_active ? 'Deactivate' : 'Activate'}
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </div>

        <div className='flex items-center justify-between gap-2'>
          <p className='text-sm text-muted-foreground'>
            Total: {total} | Page {currentPage} / {pageCount}
          </p>
          <div className='flex items-center gap-2'>
            <Button
              variant='outline'
              disabled={currentPage <= 1}
              onClick={() =>
                navigate({
                  search: (prev) => ({ ...prev, page: (prev.page ?? 1) - 1 }),
                })
              }
            >
              Previous
            </Button>
            <Button
              variant='outline'
              disabled={currentPage >= pageCount}
              onClick={() =>
                navigate({
                  search: (prev) => ({ ...prev, page: (prev.page ?? 1) + 1 }),
                })
              }
            >
              Next
            </Button>
          </div>
        </div>
      </Main>
    </>
  )
}
