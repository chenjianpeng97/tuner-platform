import { Shield, UserCheck, User, type LucideIcon } from 'lucide-react'
import type { UserRole } from '@/api/users'

export const callTypes = new Map<'active' | 'inactive', string>([
  ['active', 'bg-teal-100/30 text-teal-900 dark:text-teal-200 border-teal-200'],
  ['inactive', 'bg-neutral-300/40 border-neutral-300'],
])

type RoleItem = {
  label: string
  value: UserRole
  icon: LucideIcon
}

export function getRoles(t: (key: string) => string): ReadonlyArray<RoleItem> {
  return [
    {
      label: t('users.roles.super_admin'),
      value: 'super_admin',
      icon: Shield,
    },
    {
      label: t('users.roles.admin'),
      value: 'admin',
      icon: UserCheck,
    },
    {
      label: t('users.roles.user'),
      value: 'user',
      icon: User,
    },
  ] as const
}
