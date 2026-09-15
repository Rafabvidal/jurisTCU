import type { ProcessoDTO } from '@/shared/types/api'
import type { ProcessCase } from '@/shared/types/cases'

const MONTHS_PER_YEAR = 12
const MS_PER_DAY = 1000 * 60 * 60 * 24
const DAYS_PER_MONTH = 30.4375

function parseDecimal(value: string | null | undefined): number {
  if (value === null || value === undefined || value === '') return 0
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : 0
}

function diffInMonths(startISO: string, endISO: string): number {
  if (!startISO || !endISO) return 0
  const start = new Date(startISO).getTime()
  const end = new Date(endISO).getTime()
  if (!Number.isFinite(start) || !Number.isFinite(end) || end < start) return 0
  const days = (end - start) / MS_PER_DAY
  return Math.max(0, Math.round(days / DAYS_PER_MONTH))
}

export function mapProcessoDTOToProcessCase(dto: ProcessoDTO): ProcessCase {
  const analise = dto.analise

  return {
    id: dto.id,
    numeroProcesso: dto.numero_processo,
    grau: dto.grau,
    tribunal: dto.tribunal,
    classeNome: dto.classe?.nome ?? '',
    orgaoJulgadorNome: dto.orgao_julgador?.nome ?? '',
    dataAjuizamento: dto.data_ajuizamento,
    dataUltimaAtualizacao: dto.data_hora_ultima_atualizacao,
    tempoTramitacaoMeses: diffInMonths(
      dto.data_ajuizamento,
      dto.data_hora_ultima_atualizacao,
    ),
    resumoCausa: analise?.resumo ?? '',
    decisaoResumo: analise?.decisao ?? '',
    palavrasChave: analise?.palavras_chave?.map((p) => p.nome) ?? [],
    statusProcesso: analise?.status ?? null,
    desfecho: analise?.desfecho ?? null,
    resultadoReclamante: analise?.resultado_reclamante ?? null,
    valorCausa: parseDecimal(analise?.valor_causa),
    custasValorTotal: parseDecimal(analise?.custas_valor_total),
    similaridade: dto.similaridade,
  }
}

export { DAYS_PER_MONTH, MONTHS_PER_YEAR, MS_PER_DAY }

