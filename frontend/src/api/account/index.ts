import {
  changePasswordApiV1AccountPasswordPut,
  loginApiV1AccountLoginPost,
  logoutApiV1AccountLogoutDelete,
  signUpApiV1AccountSignupPost,
} from '@/api/generated/account'
import type {
  ChangePasswordRequest,
  LogInRequest,
  SignUpRequest,
  SignUpResponse,
  UserRole,
} from '@/api/generated/types'

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
  return signUpApiV1AccountSignupPost(payload)
}

export async function login(payload: LogInRequest): Promise<CurrentUserFallback> {
  await loginApiV1AccountLoginPost(payload)
  return {
    username: payload.username,
    role: FALLBACK_CURRENT_USER.role,
    exp: Date.now() + 24 * 60 * 60 * 1000,
  }
}

export async function logout(): Promise<void> {
  await logoutApiV1AccountLogoutDelete()
}

export async function changePassword(payload: ChangePasswordRequest): Promise<void> {
  await changePasswordApiV1AccountPasswordPut(payload)
}
