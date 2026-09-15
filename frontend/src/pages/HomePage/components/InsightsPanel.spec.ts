import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import type { HomeInsights } from '@/shared/types/cases'

import InsightsPanel from './InsightsPanel.vue'

function buildInsights(overrides: Partial<HomeInsights> = {}): HomeInsights {
  return {
    kpis: {
      totalCases: 3,
      valorMedio: 4000,
      valorTotal: 12000,
      valorMaximo: 6000,
      taxaProcedencia: 67,
      taxaGanhoReclamante: 67,
      tempoMedioMeses: 12,
      palavrasChavesRelevantes: ['horas_extras', 'jornada'],
    },
    desfechoSeries: {
      labels: ['Procedente', 'Improcedente'],
      values: [2, 1],
    },
    statusSeries: {
      labels: ['Sentenciado'],
      values: [3],
    },
    resultadoSeries: {
      labels: ['Ganhou', 'Perdeu'],
      values: [2, 1],
    },
    valorRadial: { atual: 4000, maximo: 6000, percentual: 67 },
    ...overrides,
  }
}

describe('InsightsPanel', () => {
  it('renderiza o título do painel e a taxa de procedência', () => {
    const wrapper = mount(InsightsPanel, {
      props: { insights: buildInsights() },
    })

    expect(wrapper.text()).toContain('Painel de insights')
    expect(wrapper.text()).toContain('67%')
  })

  it('renderiza os 4 charts (desfecho, resultado, valor, status) com stub', () => {
    const wrapper = mount(InsightsPanel, {
      props: { insights: buildInsights() },
    })

    const stubs = wrapper.findAllComponents({ name: 'ApexchartStub' })
    expect(stubs.length).toBe(4)
  })

  it('renderiza fallback textual quando não há dados de desfecho', () => {
    const insights = buildInsights({
      desfechoSeries: { labels: [], values: [] },
      statusSeries: { labels: [], values: [] },
      resultadoSeries: { labels: [], values: [] },
      valorRadial: { atual: 0, maximo: 0, percentual: 0 },
    })

    const wrapper = mount(InsightsPanel, { props: { insights } })

    expect(wrapper.findAllComponents({ name: 'ApexchartStub' })).toHaveLength(0)
    expect(wrapper.text()).toContain('Sem desfechos registrados')
  })

  it('lista as palavras-chave em argumentos relevantes', () => {
    const wrapper = mount(InsightsPanel, {
      props: { insights: buildInsights() },
    })

    expect(wrapper.text()).toContain('horas_extras')
    expect(wrapper.text()).toContain('jornada')
  })
})
