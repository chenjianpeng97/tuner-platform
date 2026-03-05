import { type Table } from '@tanstack/react-table'
import { ShieldCheck, ShieldX, UserCheck, UserX } from 'lucide-react'
import { useTranslation } from 'react-i18next'
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
  const { t } = useTranslation('business')
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
        success: t('users.bulk.completed', { label }),
        error: t('users.bulk.failed', { label }),
      }
    )
  }

  const activateUsers = async () => {
    await applyBulkAction(t('users.bulk.activating'), async (user) => {
      if (user.isActive) return
      await setUserActivation({ userId: user.id, isActive: true })
    })
  }

  const deactivateUsers = async () => {
    await applyBulkAction(t('users.bulk.deactivating'), async (user) => {
      if (!user.isActive || user.role === 'super_admin') return
      await setUserActivation({ userId: user.id, isActive: false })
    })
  }

  const grantAdminForUsers = async () => {
    await applyBulkAction(t('users.bulk.grantingAdmin'), async (user) => {
      if (user.role !== 'user') return
      await setUserAdmin({ userId: user.id, isAdmin: true })
    })
  }

  const revokeAdminForUsers = async () => {
    await applyBulkAction(t('users.bulk.revokingAdmin'), async (user) => {
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
            aria-label={t('users.actions.activateSelected')}
            title={t('users.actions.activateSelected')}
          >
            <UserCheck />
            <span className='sr-only'>{t('users.actions.activateSelected')}</span>
          </Button>
        </TooltipTrigger>
        <TooltipContent>
          <p>{t('users.actions.activateSelected')}</p>
        </TooltipContent>
      </Tooltip>

      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant='outline'
            size='icon'
            onClick={deactivateUsers}
            className='size-8'
            aria-label={t('users.actions.deactivateSelected')}
            title={t('users.actions.deactivateSelected')}
          >
            <UserX />
            <span className='sr-only'>{t('users.actions.deactivateSelected')}</span>
          </Button>
        </TooltipTrigger>
        <TooltipContent>
          <p>{t('users.actions.deactivateSelected')}</p>
        </TooltipContent>
      </Tooltip>

      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant='outline'
            size='icon'
            onClick={grantAdminForUsers}
            className='size-8'
            aria-label={t('users.actions.grantAdminSelected')}
            title={t('users.actions.grantAdminSelected')}
          >
            <ShieldCheck />
            <span className='sr-only'>{t('users.actions.grantAdminSelected')}</span>
          </Button>
        </TooltipTrigger>
        <TooltipContent>
          <p>{t('users.actions.grantAdminSelected')}</p>
        </TooltipContent>
      </Tooltip>

      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant='outline'
            size='icon'
            onClick={revokeAdminForUsers}
            className='size-8'
            aria-label={t('users.actions.revokeAdminSelected')}
            title={t('users.actions.revokeAdminSelected')}
          >
            <ShieldX />
            <span className='sr-only'>{t('users.actions.revokeAdminSelected')}</span>
          </Button>
        </TooltipTrigger>
        <TooltipContent>
          <p>{t('users.actions.revokeAdminSelected')}</p>
        </TooltipContent>
      </Tooltip>
    </BulkActionsToolbar>
  )
}
