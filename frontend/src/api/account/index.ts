import {
  getAccount,
} from '@/api/generated/account/account'
import type {
  BodyChangePasswordApiV1AccountPasswordPut as ChangePasswordRequest,
  LogInRequest,
  SignUpRequest,
  SignUpResponse,
  UserRole,
} from '@/api/generated/models'

const accountApi = getAccount()

export interface CurrentUserFallback {
  username: string
  role: UserRole
  exp: number
}

export const FALLBACK_CURRENT_USER: CurrentUserFallback = {
  username: 'mock_user',
  role: 'user',
  exp: Date.now() + 24 * 60 * 60 * 1000,
}

export async function signUp(payload: SignUpRequest): Promise<SignUpResponse> {
  return accountApi.signUpApiV1AccountSignupPost(payload)
}

export async function login(payload: LogInRequest): Promise<CurrentUserFallback> {
  await accountApi.loginApiV1AccountLoginPost(payload)
  return {
    username: payload.username,
    role: FALLBACK_CURRENT_USER.role,
    exp: Date.now() + 24 * 60 * 60 * 1000,
  }
}

export async function logout(): Promise<void> {
  await accountApi.logoutApiV1AccountLogoutDelete()
}

export async function changePassword(payload: ChangePasswordRequest): Promise<void> {
  await accountApi.changePasswordApiV1AccountPasswordPut(payload)
}
