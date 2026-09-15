import type { ProcessCase } from '@/shared/types/cases'
import { describe, expect, it } from 'vitest'
import { buildHomeInsights } from './useHomeInsights'


function buildCase(overrides: Partial<ProcessCase> = {}): ProcessCase {
  return {
    id: 1,
    numeroProcesso: '0001',
    grau: 'G1',
    tribunal: 'TRT6',
    classeNome: 'Reclamação',
    orgaoJulgadorNome: '5ª JCJ',
    dataAjuizamento: '2024-01-01',
    dataUltimaAtualizacao: '2024-09-01',
    tempoTramitacaoMeses: 8,
    resumoCausa: '',
    decisaoResumo: '',
    palavrasChave: ['horas_extras'],
    statusProcesso: 'sentenciado',
    desfecho: 'sentenca_procedente',
    resultadoReclamante: 'ganhou',
    valorCausa: 1000,
    custasValorTotal: 100,
    similaridade: 0.9,
    ...overrides,
  }
}

describe('buildHomeInsights', () => {
  it('retorna estado vazio quando não há casos', () => {
    const result = buildHomeInsights([])

    expect(result.kpis.totalCases).toBe(0)
    expect(result.kpis.valorMedio).toBe(0)
    expect(result.desfechoSeries.values).toEqual([])
    expect(result.statusSeries.values).toEqual([])
    expect(result.resultadoSeries.values).toEqual([])
  })

  it('calcula KPIs agregados (valor médio, taxa de procedência, ganho)', () => {
    const items: ProcessCase[] = [
      buildCase({ valorCausa: 2000, desfecho: 'sentenca_procedente', resultadoReclamante: 'ganhou' }),
      buildCase({ valorCausa: 4000, desfecho: 'sentenca_improcedente', resultadoReclamante: 'perdeu' }),
      buildCase({ valorCausa: 6000, desfecho: 'acordo_favoravel', resultadoReclamante: 'ganhou_parcial' }),
    ]

    const result = buildHomeInsights(items)

    expect(result.kpis.totalCases).toBe(3)
    expect(result.kpis.valorMedio).toBe(4000)
    expect(result.kpis.valorTotal).toBe(12000)
    expect(result.kpis.valorMaximo).toBe(6000)
    expect(result.kpis.taxaProcedencia).toBe(67)
    expect(result.kpis.taxaGanhoReclamante).toBe(67)
  })

  it('agrega contagem por desfecho, status e resultado ordenadas desc', () => {
    const items: ProcessCase[] = [
      buildCase({ desfecho: 'sentenca_procedente', statusProcesso: 'sentenciado', resultadoReclamante: 'ganhou' }),
      buildCase({ desfecho: 'sentenca_procedente', statusProcesso: 'sentenciado', resultadoReclamante: 'ganhou' }),
      buildCase({ desfecho: 'sentenca_improcedente', statusProcesso: 'arquivado', resultadoReclamante: 'perdeu' }),
    ]

    const result = buildHomeInsights(items)

    expect(result.desfechoSeries.values[0]).toBe(2)
    expect(result.desfechoSeries.labels[0]).toBe('Procedente')
    expect(result.statusSeries.values).toEqual([2, 1])
    expect(result.resultadoSeries.values).toEqual([2, 1])
  })

  it('extrai top palavras-chave normalizadas e ordenadas', () => {
    const items: ProcessCase[] = [
      buildCase({ palavrasChave: ['HORAS_EXTRAS', 'jornada'] }),
      buildCase({ palavrasChave: ['horas_extras', 'JORNADA', 'multa'] }),
      buildCase({ palavrasChave: ['horas_extras'] }),
    ]

    const result = buildHomeInsights(items)

    expect(result.kpis.palavrasChavesRelevantes[0]).toBe('horas_extras')
    expect(result.kpis.palavrasChavesRelevantes).toContain('jornada')
    expect(result.kpis.palavrasChavesRelevantes).toContain('multa')
  })

  it('calcula valorRadial com percentual proporcional ao máximo', () => {
    const items: ProcessCase[] = [
      buildCase({ valorCausa: 1000 }),
      buildCase({ valorCausa: 9000 }),
    ]

    const result = buildHomeInsights(items)

    expect(result.valorRadial.atual).toBe(5000)
    expect(result.valorRadial.maximo).toBe(9000)
    expect(result.valorRadial.percentual).toBe(56)
  })

  it('ignora casos sem desfecho/resultado nas taxas', () => {
    const items: ProcessCase[] = [
      buildCase({ desfecho: null, resultadoReclamante: null }),
      buildCase({ desfecho: 'sentenca_procedente', resultadoReclamante: 'ganhou' }),
    ]

    const result = buildHomeInsights(items)

    expect(result.kpis.taxaProcedencia).toBe(100)
    expect(result.kpis.taxaGanhoReclamante).toBe(100)
  })
})
