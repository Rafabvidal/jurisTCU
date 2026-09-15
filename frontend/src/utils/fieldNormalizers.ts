/**
 * Field normalizers - Map enum values to human-readable display labels
 */

// General formatter to handle fallbacks for camelCase and snake_case
function formatRawValueToLabel(value: string): string {
  const words = value
    .replace(/_/g, ' ')
    .replace(/([A-Z])/g, ' $1')
    .trim()
    .split(/\s+/)
  
  return words
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')
}

// Status mapping
const STATUS_NORMALIZERS: Record<string, string> = {
  sentenciado: 'Sentenciado',
  sentenciadoEmRecurso: 'Sentenciado em Recurso',
  emAlegacoes: 'Em Alegações',
  suspenso: 'Suspenso',
  cancelado: 'Cancelado',
  arquivado: 'Arquivado',
  ativo: 'Ativo',
  inativo: 'Inativo',
  em_andamento: 'Em Andamento',
  acordo_homologado: 'Acordo Homologado',
}

// Resultado reclamante mapping
const RESULTADO_RECLAMANTE_NORMALIZERS: Record<string, string> = {
  ganhou: 'Ganhou',
  ganhou_total: 'Ganhou Total',
  ganhou_parcial: 'Ganhou Parcial',
  perdeu: 'Perdeu',
  desistiu: 'Desistiu',
  sem_resultado: 'Sem Resultado',
  extinto: 'Extinto',
  sem_decisao: 'Sem Decisão',
}

// Desfecho mapping
const DESFECHO_NORMALIZERS: Record<string, string> = {
  acordo_favoravel: 'Acordo Favorável',
  sentenca_procedente: 'Sentença Procedente',
  sentenca_parcialmente_procedente: 'Sentença Parcialmente Procedente',
  sentenca_improcedente: 'Sentença Improcedente',
  sentenca_extinto: 'Sentença Extinto',
  recurso_provido: 'Recurso Provido',
  recurso_provido_parcialmente: 'Recurso Provido Parcialmente',
  recurso_improvido: 'Recurso Improvido',
  homologado: 'Homologado',
  acordo: 'Acordo',
  extinta: 'Extinta',
  arquivado_sem_decisao: 'Arquivado Sem Decisão',
  outro: 'Outro',
}

/**
 * Normalize status value to display label
 */
export function normalizeStatus(value?: string | null): string {
  if (!value) return 'Não informado'
  return STATUS_NORMALIZERS[value] || formatRawValueToLabel(value)
}

/**
 * Normalize resultado_reclamante value to display label
 */
export function normalizeResultadoReclamante(value?: string | null): string {
  if (!value) return 'Não informado'
  return RESULTADO_RECLAMANTE_NORMALIZERS[value] || formatRawValueToLabel(value)
}

/**
 * Normalize desfecho value to display label
 */
export function normalizeDesfecho(value?: string | null): string {
  if (!value) return 'Não informado'
  return DESFECHO_NORMALIZERS[value] || formatRawValueToLabel(value)
}
