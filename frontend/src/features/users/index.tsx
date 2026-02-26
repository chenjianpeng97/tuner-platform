import { DotsHorizontalIcon } from '@radix-ui/react-icons'
import {
  type ColumnDef,
  type PaginationState,
  type SortingState,
  type VisibilityState,
  flexRender,
  functionalUpdate,
  getCoreRowModel,
  useReactTable,
} from '@tanstack/react-table'
import { useMemo, useState } from 'react'
import { getRouteApi } from '@tanstack/react-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { ConfigDrawer } from '@/components/config-drawer'
import { DataTableColumnHeader, DataTablePagination } from '@/components/data-table'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { PasswordInput } from '@/components/password-input'
import { ProfileDropdown } from '@/components/profile-dropdown'
import { Search } from '@/components/search'
import { ThemeSwitch } from '@/components/theme-switch'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
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
  type UserQueryModel,
  toRoleLabel,
  toStatusLabel,
  type UserRole,
} from '@/api/users'

const route = getRouteApi('/_authenticated/users/')

function sortingFieldToColumnId(sortingField: string) {
  if (sortingField === 'role') return 'role'
  if (sortingField === 'is_active') return 'status'
  return 'username'
}

function columnIdToSortingField(columnId: string) {
  if (columnId === 'role') return 'role'
  if (columnId === 'status') return 'is_active'
  return 'username'
}

type PasswordDialogState = {
  userId: string
  username: string
} | null

export function Users() {
  const search = route.useSearch()
  const navigate = route.useNavigate()
  const queryClient = useQueryClient()

  const [createSheetOpen, setCreateSheetOpen] = useState(false)
  const [newUsername, setNewUsername] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [newConfirmPassword, setNewConfirmPassword] = useState('')
  const [newRole, setNewRole] = useState<UserRole>('user')
  const [passwordDialog, setPasswordDialog] = useState<PasswordDialogState>(null)
  const [resetPassword, setResetPassword] = useState('')
  const [resetConfirmPassword, setResetConfirmPassword] = useState('')
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({})
  const [sorting, setSorting] = useState<SortingState>([
    {
      id: sortingFieldToColumnId(search.sortingField ?? 'username'),
      desc: (search.sortingOrder ?? 'ASC') === 'DESC',
    },
  ])

  const queryInput = useMemo(
    () => ({
      page: search.page ?? 1,
      pageSize: search.pageSize ?? 10,
      sortingField: search.sortingField ?? 'username',
      sortingOrder: search.sortingOrder ?? 'ASC',
    }),
    [search.page, search.pageSize, search.sortingField, search.sortingOrder]
  )

  const pagination = useMemo<PaginationState>(
    () => ({
      pageIndex: Math.max((search.page ?? 1) - 1, 0),
      pageSize: search.pageSize ?? 10,
    }),
    [search.page, search.pageSize]
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
      setNewConfirmPassword('')
      setNewRole('user')
      setCreateSheetOpen(false)
      await refreshUsers()
    },
  })

  const setPasswordMutation = useMutation({
    mutationFn: ({ userId, password }: { userId: string; password: string }) =>
      setUserPassword(userId, password),
    onSuccess: () => {
      toast.success('Password updated')
      setPasswordDialog(null)
      setResetPassword('')
      setResetConfirmPassword('')
    },
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

  const onPaginationChange = (
    updater: PaginationState | ((old: PaginationState) => PaginationState)
  ) => {
    const next = functionalUpdate(updater, pagination)
    navigate({
      search: (prev) => ({
        ...prev,
        page: next.pageIndex + 1,
        pageSize: next.pageSize,
      }),
    })
  }

  const onSortingChange = (
    updater: SortingState | ((old: SortingState) => SortingState)
  ) => {
    const next = functionalUpdate(updater, sorting)
    setSorting(next)

    const firstSort = next[0]
    navigate({
      search: (prev) => ({
        ...prev,
        page: 1,
        sortingField: columnIdToSortingField(firstSort?.id ?? 'username'),
        sortingOrder: firstSort?.desc ? 'DESC' : 'ASC',
      }),
    })
  }

  const onCreateUser = () => {
    if (!newUsername.trim() || !newPassword.trim()) {
      toast.error('Username and password are required')
      return
    }

    if (newPassword !== newConfirmPassword) {
      toast.error('Password and confirm password do not match')
      return
    }

    createUserMutation.mutate({
      username: newUsername.trim(),
      password: newPassword,
      role: newRole,
    })
  }

  const onSubmitPasswordReset = () => {
    if (!passwordDialog) return

    if (!resetPassword.trim()) {
      toast.error('Password is required')
      return
    }

    if (resetPassword !== resetConfirmPassword) {
      toast.error('Password and confirm password do not match')
      return
    }

    setPasswordMutation.mutate({ userId: passwordDialog.userId, password: resetPassword })
  }

  const columns = useMemo<ColumnDef<UserQueryModel>[]>(
    () => [
      {
        accessorKey: 'username',
        header: ({ column }) => <DataTableColumnHeader column={column} title='Username' />,
        cell: ({ row }) => <span>{row.original.username}</span>,
      },
      {
        id: 'role',
        accessorFn: (row) => row.role,
        header: ({ column }) => <DataTableColumnHeader column={column} title='Role' />,
        cell: ({ row }) => <span>{toRoleLabel(row.original.role)}</span>,
      },
      {
        id: 'status',
        accessorFn: (row) => (row.is_active ? 'Active' : 'Inactive'),
        header: ({ column }) => <DataTableColumnHeader column={column} title='Status' />,
        cell: ({ row }) => <span>{toStatusLabel(row.original)}</span>,
      },
      {
        id: 'actions',
        enableSorting: false,
        enableHiding: false,
        cell: ({ row }) => (
          <DropdownMenu modal={false}>
            <DropdownMenuTrigger asChild>
              <Button variant='ghost' className='flex h-8 w-8 p-0 data-[state=open]:bg-muted'>
                <DotsHorizontalIcon className='h-4 w-4' />
                <span className='sr-only'>Open menu</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align='end' className='w-[190px]'>
              <DropdownMenuItem
                onClick={() =>
                  setPasswordDialog({
                    userId: row.original.id_,
                    username: row.original.username,
                  })
                }
              >
                Set Password
              </DropdownMenuItem>
              <DropdownMenuItem
                disabled={!canToggleAdmin(row.original.role) || toggleAdminMutation.isPending}
                onClick={() =>
                  toggleAdminMutation.mutate({
                    userId: row.original.id_,
                    role: row.original.role,
                  })
                }
              >
                {isAdminRole(row.original.role) ? 'Revoke Admin' : 'Grant Admin'}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                disabled={toggleActivationMutation.isPending}
                onClick={() =>
                  toggleActivationMutation.mutate({
                    userId: row.original.id_,
                    isActive: row.original.is_active,
                  })
                }
              >
                {row.original.is_active ? 'Deactivate' : 'Activate'}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ),
      },
    ],
    [toggleActivationMutation, toggleAdminMutation]
  )

  // eslint-disable-next-line react-hooks/incompatible-library
  const table = useReactTable({
    data: users,
    columns,
    state: {
      sorting,
      pagination,
      columnVisibility,
    },
    pageCount,
    manualPagination: true,
    manualSorting: true,
    onPaginationChange,
    onSortingChange,
    onColumnVisibilityChange: setColumnVisibility,
    getCoreRowModel: getCoreRowModel(),
  })

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
          <Button onClick={() => setCreateSheetOpen(true)}>
            Create User
          </Button>
        </div>

        <div className='overflow-hidden rounded-md border'>
          <Table>
            <TableHeader>
              {table.getHeaderGroups().map((headerGroup) => (
                <TableRow key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <TableHead key={header.id}>
                      {header.isPlaceholder
                        ? null
                        : flexRender(header.column.columnDef.header, header.getContext())}
                    </TableHead>
                  ))}
                </TableRow>
              ))}
            </TableHeader>
            <TableBody>
              {usersQuery.isLoading && (
                <TableRow>
                  <TableCell colSpan={columns.length}>Loading...</TableCell>
                </TableRow>
              )}

              {!usersQuery.isLoading && users.length === 0 && (
                <TableRow>
                  <TableCell colSpan={columns.length}>No users found</TableCell>
                </TableRow>
              )}

              {!usersQuery.isLoading &&
                table.getRowModel().rows.map((row) => (
                  <TableRow key={row.id}>
                    {row.getVisibleCells().map((cell) => (
                      <TableCell key={cell.id}>
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </TableCell>
                    ))}
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </div>

        <div className='flex items-center justify-between gap-2 text-sm text-muted-foreground'>
          <p className='text-sm text-muted-foreground'>
            Total: {total} | Page {currentPage} / {pageCount}
          </p>
        </div>

        <DataTablePagination table={table} className='mt-auto px-0' />
      </Main>

      <Sheet open={createSheetOpen} onOpenChange={setCreateSheetOpen}>
        <SheetContent className='flex flex-col'>
          <SheetHeader className='text-start'>
            <SheetTitle>Create User</SheetTitle>
            <SheetDescription>
              Create a user in the side drawer, aligned with the Tasks page interaction pattern.
            </SheetDescription>
          </SheetHeader>
          <div className='flex-1 space-y-4 overflow-y-auto px-4'>
            <div className='space-y-2'>
              <Label htmlFor='create-username'>Username</Label>
              <Input
                id='create-username'
                value={newUsername}
                onChange={(event) => setNewUsername(event.target.value)}
                placeholder='new_user'
              />
            </div>
            <div className='space-y-2'>
              <Label htmlFor='create-password'>Password</Label>
              <PasswordInput
                id='create-password'
                value={newPassword}
                onChange={(event) => setNewPassword(event.target.value)}
                placeholder='********'
              />
            </div>
            <div className='space-y-2'>
              <Label htmlFor='create-confirm-password'>Confirm Password</Label>
              <PasswordInput
                id='create-confirm-password'
                value={newConfirmPassword}
                onChange={(event) => setNewConfirmPassword(event.target.value)}
                placeholder='********'
              />
            </div>
            <div className='space-y-2'>
              <Label htmlFor='create-role'>Role</Label>
              <Select value={newRole} onValueChange={(value) => setNewRole(value as UserRole)}>
                <SelectTrigger id='create-role'>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value='user'>User</SelectItem>
                  <SelectItem value='admin'>Admin</SelectItem>
                  <SelectItem value='super_admin'>Super Admin</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <SheetFooter className='gap-2'>
            <SheetClose asChild>
              <Button variant='outline'>Cancel</Button>
            </SheetClose>
            <Button onClick={onCreateUser} disabled={createUserMutation.isPending}>
              Create User
            </Button>
          </SheetFooter>
        </SheetContent>
      </Sheet>

      <Dialog
        open={passwordDialog !== null}
        onOpenChange={(open) => {
          if (!open) {
            setPasswordDialog(null)
            setResetPassword('')
            setResetConfirmPassword('')
          }
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Set Password</DialogTitle>
            <DialogDescription>
              {passwordDialog
                ? `Set password for ${passwordDialog.username}.`
                : 'Set user password.'}
            </DialogDescription>
          </DialogHeader>
          <div className='space-y-4'>
            <div className='space-y-2'>
              <Label htmlFor='reset-password'>New Password</Label>
              <PasswordInput
                id='reset-password'
                value={resetPassword}
                onChange={(event) => setResetPassword(event.target.value)}
                placeholder='********'
              />
            </div>
            <div className='space-y-2'>
              <Label htmlFor='reset-confirm-password'>Confirm Password</Label>
              <PasswordInput
                id='reset-confirm-password'
                value={resetConfirmPassword}
                onChange={(event) => setResetConfirmPassword(event.target.value)}
                placeholder='********'
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant='outline' onClick={() => setPasswordDialog(null)}>
              Cancel
            </Button>
            <Button onClick={onSubmitPasswordReset} disabled={setPasswordMutation.isPending}>
              Save Password
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
