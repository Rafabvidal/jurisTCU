import { VueQueryPlugin } from '@tanstack/vue-query'
import { flushPromises, mount } from '@vue/test-utils'
import { MotionPlugin } from '@vueuse/motion'
import { createPinia } from 'pinia'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

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

import HomePage from './HomePage.vue'

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
        orgao_julgador: { codigo: 1, nome: 'JCJ Recife', codigo_municipio_ibge: null },
        assuntos: [],
        analise: {
          id: 1,
          resumo: 'Resumo',
          tipo_ato_principal: 'sentenca',
          decisao: 'Decisão procedente',
          palavras_chave: [{ id: 1, nome: 'horas_extras' }],
          status: 'sentenciado',
          desfecho: 'sentenca_procedente',
          resultado_reclamante: 'ganhou',
          valor_causa: '5000.00',
          custas_valor_total: '150.00',
        },
        similaridade: 0.95,
      },
    ],
  }
}

function buildRouter() {
  const blank = { template: '<div />' }
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: blank },
      { path: '/login', component: blank },
    ],
  })
}

function mountPage() {
  return mount(HomePage, {
    global: {
      plugins: [
        createPinia(),
        buildRouter(),
        [
          VueQueryPlugin,
          {
            queryClientConfig: {
              defaultOptions: { queries: { retry: false } },
            },
          },
        ],
        MotionPlugin,
      ],
    },
  })
}

describe('HomePage', () => {
  afterEach(() => {
    buscaSemanticaSpy.mockReset()
  })

  it('mostra empty panel inicial e não dispara busca', () => {
    const wrapper = mountPage()
    expect(wrapper.text()).toContain('Faça uma busca para iniciar')
    expect(buscaSemanticaSpy).not.toHaveBeenCalled()
  })

  it('orquestra busca semântica e renderiza ResultsList + InsightsPanel', async () => {
    buscaSemanticaSpy.mockResolvedValueOnce(buildResponse())

    const wrapper = mountPage()
    const searchBar = wrapper.findComponent({ name: 'SearchBar' })
    expect(searchBar.exists()).toBe(true)

    searchBar.vm.$emit('submit', 'horas extras')
    await flushPromises()

    expect(buscaSemanticaSpy).toHaveBeenCalledTimes(1)
    const firstCall = buscaSemanticaSpy.mock.calls[0]
    expect(firstCall?.[0].consulta).toBe('horas extras')

    expect(wrapper.findComponent({ name: 'ResultsList' }).exists()).toBe(true)
    expect(wrapper.findComponent({ name: 'InsightsPanel' }).exists()).toBe(true)
    expect(wrapper.text()).toContain('0001')
  })

  it('mostra mensagem de erro quando a busca falha', async () => {
    buscaSemanticaSpy.mockRejectedValueOnce(new Error('Servidor indisponível'))

    const wrapper = mountPage()
    wrapper.findComponent({ name: 'SearchBar' }).vm.$emit('submit', 'erro')
    await flushPromises()
    await flushPromises()

    expect(wrapper.text()).toContain('Não foi possível concluir a busca')
  })

  it('mostra empty quando a API retorna lista vazia', async () => {
    buscaSemanticaSpy.mockResolvedValueOnce({ items: [] })

    const wrapper = mountPage()
    wrapper.findComponent({ name: 'SearchBar' }).vm.$emit('submit', 'vazio')
    await flushPromises()

    expect(wrapper.text()).toContain('Nenhum processo encontrado')
  })
})
