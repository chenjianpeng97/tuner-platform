import type { UserQueryModel, UserRole } from '@/api/users'

export interface UsersRowViewModel {
  id: string
  username: string
  role: UserRole
  isActive: boolean
  statusLabel: 'active' | 'inactive'
}

export function toUsersRow(user: UserQueryModel): UsersRowViewModel {
  const isActive = user.is_active
  return {
    id: user.id_,
    username: user.username,
    role: user.role,
    isActive,
    statusLabel: isActive ? 'active' : 'inactive',
  }
}

export function toUsersRows(users: UserQueryModel[]): UsersRowViewModel[] {
  return users.map(toUsersRow)
}
