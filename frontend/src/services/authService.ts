import { API_ENDPOINTS } from '@/shared/constants/api'
import type {
  AuthResponse,
  LoginPayload,
  RegisterPayload,
  UserDTO,
} from '@/shared/types/api'

import { httpClient } from './httpClient'

export class AuthService {
  static async register(payload: RegisterPayload): Promise<AuthResponse> {
    const { data } = await httpClient.post<AuthResponse>(API_ENDPOINTS.authRegister, payload)
    return data
  }

  static async login(payload: LoginPayload): Promise<AuthResponse> {
    const { data } = await httpClient.post<AuthResponse>(API_ENDPOINTS.authLogin, payload)
    return data
  }

  static async logout(): Promise<void> {
    await httpClient.post(API_ENDPOINTS.authLogout)
  }

  static async getMe(): Promise<UserDTO> {
    const { data } = await httpClient.get<UserDTO>(API_ENDPOINTS.authMe)
    return data
  }

  static async updateMe(payload: { name: string }): Promise<UserDTO> {
    const { data } = await httpClient.patch<UserDTO>(API_ENDPOINTS.authMe, payload)
    return data
  }
}
