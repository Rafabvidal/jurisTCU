import type {
  Desfecho,
  ResultadoReclamante,
  StatusProcesso,
} from '@/shared/types/api'

export const CHART_HEIGHT = {
  donut: 300,
  bar: 220,
  radial: 220,
} as const

export const CHART_COLORS = {
  brand: '#163d77',
  brandStrong: '#0f2d57',
  brandSoft: '#dbe7ff',
  accent: '#0f766e',
  accentSoft: '#d9f4ef',
  success: '#15803d',
  warning: '#c2410c',
  danger: '#b91c1c',
  neutral: '#5d708f',
} as const

export const CHART_PALETTE_DESFECHO: string[] = [
  CHART_COLORS.success,
  CHART_COLORS.accent,
  CHART_COLORS.warning,
  CHART_COLORS.danger,
  CHART_COLORS.neutral,
  CHART_COLORS.brandSoft,
  CHART_COLORS.brand,
]

export const CHART_PALETTE_STATUS: string[] = [
  CHART_COLORS.brand,
  CHART_COLORS.accent,
  CHART_COLORS.warning,
  CHART_COLORS.neutral,
]

export const CHART_PALETTE_RESULTADO: string[] = [
  CHART_COLORS.success,
  CHART_COLORS.accent,
  CHART_COLORS.danger,
  CHART_COLORS.neutral,
]

export const CHART_PALETTE_RADIAL: string[] = [CHART_COLORS.brand]

export const CHART_FONT_FAMILY = "'Manrope', 'Segoe UI', sans-serif"

export const DESFECHO_LABELS: Record<Desfecho, string> = {
  acordo_favoravel: 'Acordo favorável',
  sentenca_procedente: 'Procedente',
  sentenca_parcialmente_procedente: 'Parcialmente procedente',
  sentenca_improcedente: 'Improcedente',
  extinta: 'Extinta',
  arquivado_sem_decisao: 'Arquivada sem decisão',
  outro: 'Outro',
}

export const STATUS_LABELS: Record<StatusProcesso, string> = {
  arquivado: 'Arquivado',
  acordo_homologado: 'Acordo homologado',
  sentenciado: 'Sentenciado',
  em_andamento: 'Em andamento',
}

export const RESULTADO_RECLAMANTE_LABELS: Record<ResultadoReclamante, string> = {
  ganhou: 'Ganhou',
  ganhou_parcial: 'Ganhou parcial',
  perdeu: 'Perdeu',
  sem_decisao: 'Sem decisão',
}

export const DESFECHOS_PROCEDENTES: ReadonlySet<Desfecho> = new Set<Desfecho>([
  'acordo_favoravel',
  'sentenca_procedente',
  'sentenca_parcialmente_procedente',
])

export const RESULTADOS_GANHO: ReadonlySet<ResultadoReclamante> = new Set<ResultadoReclamante>([
  'ganhou',
  'ganhou_parcial',
])

export const TOP_PALAVRAS_CHAVE_LIMIT = 5
