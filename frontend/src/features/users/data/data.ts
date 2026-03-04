import { Shield, UserCheck, User, type LucideIcon } from 'lucide-react'
import type { UserRole } from '@/api/users'

export const callTypes = new Map<'active' | 'inactive', string>([
  ['active', 'bg-teal-100/30 text-teal-900 dark:text-teal-200 border-teal-200'],
  ['inactive', 'bg-neutral-300/40 border-neutral-300'],
])

export const roles = [
  {
    label: 'Super Admin',
    value: 'super_admin',
    icon: Shield,
  },
  {
    label: 'Admin',
    value: 'admin',
    icon: UserCheck,
  },
  {
    label: 'User',
    value: 'user',
    icon: User,
  },
] as const satisfies ReadonlyArray<{
  label: string
  value: UserRole
  icon: LucideIcon
}>
