import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import type { ProcessCase } from '@/shared/types/cases'

import ResultCard from './ResultCard.vue'

function buildCase(overrides: Partial<ProcessCase> = {}): ProcessCase {
  return {
    id: 1,
    numeroProcesso: '0000256-48.2025.5.06.0171',
    grau: 'G1',
    tribunal: 'TRT6',
    classeNome: 'Reclamação Trabalhista',
    orgaoJulgadorNome: '23A VARA',
    dataAjuizamento: '2025-01-01',
    dataUltimaAtualizacao: '2025-05-01',
    tempoTramitacaoMeses: 4,
    resumoCausa: 'Resumo',
    decisaoResumo: 'Decisão resumida',
    palavrasChave: ['horas_extras'],
    statusProcesso: null,
    desfecho: null,
    resultadoReclamante: null,
    valorCausa: 1000,
    custasValorTotal: 0,
    similaridade: 57,
    ...overrides,
  }
}

describe('ResultCard', () => {
  it('renderiza link interno de detalhe e link externo para o TRT-6', () => {
    const wrapper = mount(ResultCard, {
      props: { item: buildCase() },
      global: {
        stubs: {
          RouterLink: {
            props: ['to'],
            template: '<a class="detail-process-link"><slot /></a>',
          },
        },
      },
    })

    const detailLink = wrapper.get('a.detail-process-link')
    expect(detailLink.text()).toContain('Ver detalhes do processo')

    const link = wrapper.get('a.external-process-link')
    expect(link.attributes('href')).toBe(
      'https://pje.trt6.jus.br/consultaprocessual/detalhe-processo/0000256-48.2025.5.06.0171',
    )
    expect(link.attributes('target')).toBe('_blank')
    expect(link.attributes('rel')).toContain('noopener')
    expect(link.attributes('title')).toContain('Você sairá da aplicação')
  })
})