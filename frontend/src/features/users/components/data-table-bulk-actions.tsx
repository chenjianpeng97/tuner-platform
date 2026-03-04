import { type Table } from '@tanstack/react-table'
import { ShieldCheck, ShieldX, UserCheck, UserX } from 'lucide-react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { DataTableBulkActions as BulkActionsToolbar } from '@/components/data-table'
import { type UsersRowViewModel } from '../model'
import { useUsers } from './users-provider'

type DataTableBulkActionsProps = {
  table: Table<UsersRowViewModel>
}

export function DataTableBulkActions({ table }: DataTableBulkActionsProps) {
  const { setUserActivation, setUserAdmin, refreshUsers } = useUsers()
  const selectedRows = table.getFilteredSelectedRowModel().rows
  const selectedUsers = selectedRows.map((row) => row.original)

  const applyBulkAction = async (
    label: string,
    worker: (user: UsersRowViewModel) => Promise<void>
  ) => {
    if (selectedUsers.length === 0) return

    await toast.promise(
      Promise.all(selectedUsers.map(worker)).then(async () => {
        await refreshUsers()
        table.resetRowSelection()
      }),
      {
        loading: `${label}...`,
        success: `${label} completed`,
        error: `${label} failed`,
      }
    )
  }

  const activateUsers = async () => {
    await applyBulkAction('Activating users', async (user) => {
      if (user.isActive) return
      await setUserActivation({ userId: user.id, isActive: true })
    })
  }

  const deactivateUsers = async () => {
    await applyBulkAction('Deactivating users', async (user) => {
      if (!user.isActive || user.role === 'super_admin') return
      await setUserActivation({ userId: user.id, isActive: false })
    })
  }

  const grantAdminForUsers = async () => {
    await applyBulkAction('Granting admin', async (user) => {
      if (user.role !== 'user') return
      await setUserAdmin({ userId: user.id, isAdmin: true })
    })
  }

  const revokeAdminForUsers = async () => {
    await applyBulkAction('Revoking admin', async (user) => {
      if (user.role !== 'admin') return
      await setUserAdmin({ userId: user.id, isAdmin: false })
    })
  }

  return (
    <BulkActionsToolbar table={table} entityName='user'>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant='outline'
            size='icon'
            onClick={activateUsers}
            className='size-8'
            aria-label='Activate selected users'
            title='Activate selected users'
          >
            <UserCheck />
            <span className='sr-only'>Activate selected users</span>
          </Button>
        </TooltipTrigger>
        <TooltipContent>
          <p>Activate selected users</p>
        </TooltipContent>
      </Tooltip>

      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant='outline'
            size='icon'
            onClick={deactivateUsers}
            className='size-8'
            aria-label='Deactivate selected users'
            title='Deactivate selected users'
          >
            <UserX />
            <span className='sr-only'>Deactivate selected users</span>
          </Button>
        </TooltipTrigger>
        <TooltipContent>
          <p>Deactivate selected users</p>
        </TooltipContent>
      </Tooltip>

      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant='outline'
            size='icon'
            onClick={grantAdminForUsers}
            className='size-8'
            aria-label='Grant admin for selected users'
            title='Grant admin for selected users'
          >
            <ShieldCheck />
            <span className='sr-only'>Grant admin for selected users</span>
          </Button>
        </TooltipTrigger>
        <TooltipContent>
          <p>Grant admin for selected users</p>
        </TooltipContent>
      </Tooltip>

      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant='outline'
            size='icon'
            onClick={revokeAdminForUsers}
            className='size-8'
            aria-label='Revoke admin for selected users'
            title='Revoke admin for selected users'
          >
            <ShieldX />
            <span className='sr-only'>Revoke admin for selected users</span>
          </Button>
        </TooltipTrigger>
        <TooltipContent>
          <p>Revoke admin for selected users</p>
        </TooltipContent>
      </Tooltip>
    </BulkActionsToolbar>
  )
}
