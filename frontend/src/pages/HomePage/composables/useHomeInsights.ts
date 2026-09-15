import { computed, type ComputedRef, type Ref } from 'vue'

import {
  DESFECHOS_PROCEDENTES,
  DESFECHO_LABELS,
  RESULTADOS_GANHO,
  RESULTADO_RECLAMANTE_LABELS,
  STATUS_LABELS,
  TOP_PALAVRAS_CHAVE_LIMIT,
} from '@/shared/constants/charts'
import type {
  Desfecho,
  ResultadoReclamante,
  StatusProcesso,
} from '@/shared/types/api'
import type {
  ChartSeries,
  HomeInsights,
  InsightKpis,
  ProcessCase,
  ValorRadial,
} from '@/shared/types/cases'

function countBy<K extends string>(
  items: ProcessCase[],
  selector: (item: ProcessCase) => K | null,
): Map<K, number> {
  const counts = new Map<K, number>()
  for (const item of items) {
    const key = selector(item)
    if (key === null) continue
    counts.set(key, (counts.get(key) ?? 0) + 1)
  }
  return counts
}

function toChartSeries<K extends string>(
  counts: Map<K, number>,
  labels: Record<K, string>,
): ChartSeries {
  const entries = Array.from(counts.entries()).sort(
    ([, a], [, b]) => b - a,
  )
  return {
    labels: entries.map(([key]) => labels[key]),
    values: entries.map(([, value]) => value),
  }
}

function average(values: number[]): number {
  if (values.length === 0) return 0
  const sum = values.reduce((acc, value) => acc + value, 0)
  return sum / values.length
}

function topKeywords(items: ProcessCase[], limit: number): string[] {
  const counts = new Map<string, number>()
  for (const item of items) {
    for (const palavra of item.palavrasChave) {
      const normalized = palavra.trim().toLowerCase()
      if (!normalized) continue
      counts.set(normalized, (counts.get(normalized) ?? 0) + 1)
    }
  }
  return Array.from(counts.entries())
    .sort(([, a], [, b]) => b - a)
    .slice(0, limit)
    .map(([key]) => key)
}

function buildKpis(items: ProcessCase[]): InsightKpis {
  if (items.length === 0) {
    return {
      totalCases: 0,
      valorMedio: 0,
      valorTotal: 0,
      valorMaximo: 0,
      taxaProcedencia: 0,
      taxaGanhoReclamante: 0,
      tempoMedioMeses: 0,
      palavrasChavesRelevantes: [],
    }
  }

  const valores = items.map((item) => item.valorCausa)
  const tempos = items.map((item) => item.tempoTramitacaoMeses)

  const desfechosValidos = items.filter((item) => item.desfecho !== null)
  const procedentes = desfechosValidos.filter(
    (item) => item.desfecho !== null && DESFECHOS_PROCEDENTES.has(item.desfecho),
  ).length

  const resultadosValidos = items.filter(
    (item) => item.resultadoReclamante !== null,
  )
  const ganhos = resultadosValidos.filter(
    (item) =>
      item.resultadoReclamante !== null &&
      RESULTADOS_GANHO.has(item.resultadoReclamante),
  ).length

  return {
    totalCases: items.length,
    valorMedio: average(valores),
    valorTotal: valores.reduce((acc, value) => acc + value, 0),
    valorMaximo: Math.max(...valores, 0),
    taxaProcedencia:
      desfechosValidos.length === 0
        ? 0
        : Math.round((procedentes / desfechosValidos.length) * 100),
    taxaGanhoReclamante:
      resultadosValidos.length === 0
        ? 0
        : Math.round((ganhos / resultadosValidos.length) * 100),
    tempoMedioMeses: Math.round(average(tempos)),
    palavrasChavesRelevantes: topKeywords(items, TOP_PALAVRAS_CHAVE_LIMIT),
  }
}

function buildValorRadial(items: ProcessCase[]): ValorRadial {
  const valores = items.map((item) => item.valorCausa)
  const atual = average(valores)
  const maximo = Math.max(...valores, 0)
  const percentual = maximo === 0 ? 0 : Math.round((atual / maximo) * 100)
  return { atual, maximo, percentual }
}

export function buildHomeInsights(items: ProcessCase[]): HomeInsights {
  const desfechoCounts = countBy<Desfecho>(items, (item) => item.desfecho)
  const statusCounts = countBy<StatusProcesso>(items, (item) => item.statusProcesso)
  const resultadoCounts = countBy<ResultadoReclamante>(
    items,
    (item) => item.resultadoReclamante,
  )

  return {
    kpis: buildKpis(items),
    desfechoSeries: toChartSeries(desfechoCounts, DESFECHO_LABELS),
    statusSeries: toChartSeries(statusCounts, STATUS_LABELS),
    resultadoSeries: toChartSeries(resultadoCounts, RESULTADO_RECLAMANTE_LABELS),
    valorRadial: buildValorRadial(items),
  }
}

export function useHomeInsights(
  cases: Ref<ProcessCase[] | undefined> | ComputedRef<ProcessCase[] | undefined>,
): ComputedRef<HomeInsights> {
  return computed(() => buildHomeInsights(cases.value ?? []))
}
