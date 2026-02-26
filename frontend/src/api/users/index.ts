import {
  activateUserApiV1UsersUserIdActivationPut,
  createUserApiV1UsersPost,
  deactivateUserApiV1UsersUserIdActivationDelete,
  grantAdminApiV1UsersUserIdRolesAdminPut,
  listUsersApiV1UsersGet,
  revokeAdminApiV1UsersUserIdRolesAdminDelete,
  setUserPasswordApiV1UsersUserIdPasswordPut,
  type ListUsersParams,
} from '@/api/generated/users'
import type {
  CreateUserRequestPydantic,
  CreateUserResponse,
  ListUsersQM,
  SortingOrder,
  UserQueryModel,
  UserRole,
} from '@/api/generated/types'

export type { UserQueryModel, UserRole }

export interface UsersQueryInput {
  page: number
  pageSize: number
  sortingField: string
  sortingOrder: SortingOrder
}

export async function listUsers(input: UsersQueryInput): Promise<ListUsersQM> {
  const params: ListUsersParams = {
    limit: input.pageSize,
    offset: (input.page - 1) * input.pageSize,
    sorting_field: input.sortingField,
    sorting_order: input.sortingOrder,
  }

  return listUsersApiV1UsersGet(params)
}

export async function createUser(
  payload: CreateUserRequestPydantic
): Promise<CreateUserResponse> {
  return createUserApiV1UsersPost(payload)
}

export async function setUserPassword(userId: string, password: string): Promise<void> {
  await setUserPasswordApiV1UsersUserIdPasswordPut(userId, password)
}

export async function grantAdmin(userId: string): Promise<void> {
  await grantAdminApiV1UsersUserIdRolesAdminPut(userId)
}

export async function revokeAdmin(userId: string): Promise<void> {
  await revokeAdminApiV1UsersUserIdRolesAdminDelete(userId)
}

export async function activateUser(userId: string): Promise<void> {
  await activateUserApiV1UsersUserIdActivationPut(userId)
}

export async function deactivateUser(userId: string): Promise<void> {
  await deactivateUserApiV1UsersUserIdActivationDelete(userId)
}

export function isAdminRole(role: UserRole): boolean {
  return role === 'admin' || role === 'super_admin'
}

export function canToggleAdmin(role: UserRole): boolean {
  return role !== 'super_admin'
}

export function toRoleLabel(role: UserRole): string {
  if (role === 'super_admin') return 'Super Admin'
  if (role === 'admin') return 'Admin'
  return 'User'
}

export function toStatusLabel(user: UserQueryModel): string {
  return user.is_active ? 'Active' : 'Inactive'
}
