export const API_ENDPOINTS = {
  buscaSemantica: '/processos/busca_semantica/',
  naoPossuemAnalise: '/processos/nao_possuem_analise/',
  naoPossuemPdf: '/processos/nao_possuem_pdf/',
  deduplicar: '/processos/deduplicar/',
  adicionarAnalise: '/processos/adicionar_analise/',
  processoDetalhe: '/processos/detalhe/',
  health: '/health/',
  authRegister: '/auth/register/',
  authLogin: '/auth/login/',
  authLogout: '/auth/logout/',
  authMe: '/auth/me/',
  savedSearches: '/saved-searches/',
} as const

export const AUTH_STORAGE_KEYS = {
  token: 'justrt6.auth.token',
  user: 'justrt6.auth.user',
} as const

export const DEFAULT_TOP_K = 10
export const MIN_TOP_K = 1
export const MAX_TOP_K = 50

export const HTTP_TIMEOUT_MS = 30_000
export const QUERY_STALE_TIME_MS = 60_000
export const QUERY_DEFAULT_RETRY = 1

export const QUERY_KEYS = {
  buscaSemantica: 'busca-semantica',
  naoPossuemAnalise: 'nao-possuem-analise',
  naoPossuemPdf: 'nao-possuem-pdf',
  processoDetalhe: 'processo-detalhe',
  savedSearches: 'saved-searches',
} as const

export const ERROR_MESSAGES = {
  network: 'Não foi possível conectar ao servidor. Verifique sua conexão.',
  timeout: 'A requisição demorou demais para responder. Tente novamente.',
  unknown: 'Ocorreu um erro inesperado ao processar a requisição.',
  invalidQuery: 'Informe um texto de busca antes de prosseguir.',
} as const
