import axios, { AxiosError, type AxiosInstance } from 'axios'

import { AUTH_STORAGE_KEYS, ERROR_MESSAGES, HTTP_TIMEOUT_MS } from '@/shared/constants/api'

function resolveBaseURL(): string {
  const fromEnv = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api"
  if (!fromEnv) {
    throw new Error('VITE_API_BASE_URL não está definida. Verifique o arquivo .env.')
  }
  return fromEnv
}

export class HttpError extends Error {
  readonly status: number | null
  readonly cause?: unknown

  constructor(message: string, status: number | null, cause?: unknown) {
    super(message)
    this.name = 'HttpError'
    this.status = status
    this.cause = cause
  }
}

/** Extrai uma mensagem legível das formas comuns de erro do DRF. */
function extractMessage(data: unknown): string | undefined {
  if (!data || typeof data !== 'object') return undefined
  const record = data as Record<string, unknown>

  if (typeof record.detail === 'string') return record.detail
  if (typeof record.mensagem === 'string') return record.mensagem

  // Primeiro erro de campo (ex.: { email: ["Este e-mail já está cadastrado."] }).
  for (const value of Object.values(record)) {
    if (typeof value === 'string') return value
    if (Array.isArray(value) && typeof value[0] === 'string') return value[0]
  }
  return undefined
}

function normalizeError(error: unknown): HttpError {
  if (error instanceof AxiosError) {
    if (error.code === 'ECONNABORTED') {
      return new HttpError(ERROR_MESSAGES.timeout, null, error)
    }
    if (!error.response) {
      return new HttpError(ERROR_MESSAGES.network, null, error)
    }
    const status = error.response.status
    const message = extractMessage(error.response.data)
    return new HttpError(message ?? ERROR_MESSAGES.unknown, status, error)
  }
  return new HttpError(ERROR_MESSAGES.unknown, null, error)
}

export const httpClient: AxiosInstance = axios.create({
  baseURL: resolveBaseURL(),
  timeout: HTTP_TIMEOUT_MS,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
})

// Injeta o token de autenticação (lido do localStorage) em toda requisição.
httpClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(AUTH_STORAGE_KEYS.token)
  if (token) {
    config.headers.set('Authorization', `Token ${token}`)
  }
  return config
})

/**
 * Trata 401 de forma centralizada: desloga o usuário e o envia para /login.
 * Importes dinâmicos evitam dependência circular (store/router → services → httpClient).
 */
async function handleUnauthorized(): Promise<void> {
  const { useAuthStore } = await import('@/stores/auth')
  const { default: router } = await import('@/router')

  const authStore = useAuthStore()
  authStore.clearSession()

  if (router.currentRoute.value.path !== '/login') {
    await router.push({ path: '/login', query: { redirect: router.currentRoute.value.fullPath } })
  }
}

httpClient.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    const normalized = normalizeError(error)
    if (normalized.status === 401) {
      void handleUnauthorized()
    }
    return Promise.reject(normalized)
  },
)
