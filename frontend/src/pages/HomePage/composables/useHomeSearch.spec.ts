import { VueQueryPlugin } from '@tanstack/vue-query'
import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { createPinia } from 'pinia'
import { defineComponent, h } from 'vue'

import type { BuscaSemanticaResponse } from '@/shared/types/api'

const buscaSemanticaSpy = vi.fn<
  (payload: { consulta: string; top_k: number }) => Promise<BuscaSemanticaResponse>
>()

vi.mock('@/services/MainService', () => ({
  MainService: {
    buscaSemantica: (payload: { consulta: string; top_k: number }) =>
      buscaSemanticaSpy(payload),
  },
}))

import { useHomeSearch } from './useHomeSearch'

function buildResponse(): BuscaSemanticaResponse {
  return {
    items: [
      {
        id: 1,
        numero_processo: '0001',
        classe: { codigo: '1', nome: 'Reclamação' },
        tribunal: 'TRT6',
        data_hora_ultima_atualizacao: '2025-01-01',
        grau: 'G1',
        data_ajuizamento: '2024-01-01',
        orgao_julgador: { codigo: 1, nome: 'JCJ', codigo_municipio_ibge: null },
        assuntos: [],
        analise: {
          id: 1,
          resumo: '',
          tipo_ato_principal: 'sentenca',
          decisao: '',
          palavras_chave: [],
          status: 'sentenciado',
          desfecho: 'sentenca_procedente',
          resultado_reclamante: 'ganhou',
          valor_causa: '1000.00',
          custas_valor_total: '0.00',
        },
        similaridade: 0.9,
      },
    ],
  }
}

function mountWithQuery(setup: () => unknown) {
  const Wrapper = defineComponent({
    setup,
    render: () => h('div'),
  })
  return mount(Wrapper, {
    global: {
      plugins: [
        createPinia(),
        [
          VueQueryPlugin,
          {
            queryClientConfig: {
              defaultOptions: { queries: { retry: false } },
            },
          },
        ],
      ],
    },
  })
}

describe('useHomeSearch', () => {
  afterEach(() => {
    buscaSemanticaSpy.mockReset()
  })

  it('não dispara a busca antes de submitSearch', () => {
    mountWithQuery(() => {
      const search = useHomeSearch()
      return { search }
    })

    expect(buscaSemanticaSpy).not.toHaveBeenCalled()
  })

  it('dispara MainService.buscaSemantica com a consulta submetida', async () => {
    buscaSemanticaSpy.mockResolvedValueOnce(buildResponse())

    let api: ReturnType<typeof useHomeSearch> | undefined
    mountWithQuery(() => {
      api = useHomeSearch()
      return { api }
    })

    api!.submitSearch('horas extras')
    await flushPromises()

    expect(buscaSemanticaSpy).toHaveBeenCalledTimes(1)
    const firstCall = buscaSemanticaSpy.mock.calls[0]
    expect(firstCall?.[0].consulta).toBe('horas extras')
    expect(firstCall?.[0].top_k).toBe(10)
  })

  it('ignora submitSearch com query vazia', () => {
    let api: ReturnType<typeof useHomeSearch> | undefined
    mountWithQuery(() => {
      api = useHomeSearch()
      return { api }
    })

    api!.submitSearch('   ')

    expect(api!.hasSearched.value).toBe(false)
    expect(buscaSemanticaSpy).not.toHaveBeenCalled()
  })
})
