import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { AuthService } from '@/services/authService'
import { AUTH_STORAGE_KEYS } from '@/shared/constants/api'
import type { UserDTO } from '@/shared/types/api'

function readStoredUser(): UserDTO | null {
  const raw = localStorage.getItem(AUTH_STORAGE_KEYS.user)
  if (!raw) return null
  try {
    return JSON.parse(raw) as UserDTO
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem(AUTH_STORAGE_KEYS.token))
  const user = ref<UserDTO | null>(readStoredUser())

  const isAuthenticated = computed(() => Boolean(token.value))

  const initials = computed(() => {
    const source = user.value?.name?.trim() || user.value?.email || ''
    if (!source) return '?'
    const parts = source.split(/\s+/).filter(Boolean)
    if (parts.length >= 2) {
      return `${parts[0]!.charAt(0)}${parts[1]!.charAt(0)}`.toUpperCase()
    }
    return source.slice(0, 2).toUpperCase()
  })

  const displayName = computed(() => user.value?.name?.trim() || user.value?.email || '')

  function setSession(newToken: string, newUser: UserDTO) {
    token.value = newToken
    user.value = newUser
    localStorage.setItem(AUTH_STORAGE_KEYS.token, newToken)
    localStorage.setItem(AUTH_STORAGE_KEYS.user, JSON.stringify(newUser))
  }

  function clearSession() {
    token.value = null
    user.value = null
    localStorage.removeItem(AUTH_STORAGE_KEYS.token)
    localStorage.removeItem(AUTH_STORAGE_KEYS.user)
  }

  async function login(email: string, password: string) {
    const data = await AuthService.login({ email, password })
    setSession(data.token, data.user)
  }

  async function register(name: string, email: string, password: string) {
    const data = await AuthService.register({ name, email, password })
    setSession(data.token, data.user)
  }

  async function logout() {
    try {
      if (token.value) await AuthService.logout()
    } finally {
      clearSession()
    }
  }

  async function updateProfile(name: string) {
    const updatedUser = await AuthService.updateMe({ name })
    user.value = updatedUser
    localStorage.setItem(AUTH_STORAGE_KEYS.user, JSON.stringify(updatedUser))
  }

  /** Revalida o token persistido contra a API ao iniciar a aplicação. */
  async function initialize() {
    if (!token.value) return
    try {
      user.value = await AuthService.getMe()
      localStorage.setItem(AUTH_STORAGE_KEYS.user, JSON.stringify(user.value))
    } catch {
      // O interceptor de 401 já cuida de limpar a sessão inválida.
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    initials,
    displayName,
    setSession,
    clearSession,
    login,
    register,
    logout,
    updateProfile,
    initialize,
  }
})
