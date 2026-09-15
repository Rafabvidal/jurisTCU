import { VueQueryPlugin } from '@tanstack/vue-query'
import { flushPromises, mount } from '@vue/test-utils'
import { MotionPlugin } from '@vueuse/motion'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import type { ProcessoDetalheDTO } from '@/shared/types/api'

const detalheSpy = vi.fn<
  (numeroProcesso: string, grau: string) => Promise<ProcessoDetalheDTO>
>()

vi.mock('@/services/MainService', () => ({
  MainService: {
    obterProcessoDetalhe: (numeroProcesso: string, grau: string) =>
      detalheSpy(numeroProcesso, grau),
  },
}))

import ProcessDetailPage from './ProcessDetailPage.vue'

function buildResponse(): ProcessoDetalheDTO {
  return {
    id: 1,
    numero_processo: '0000256-48.2025.5.06.0171',
    classe: { codigo: '1800', nome: 'Reclamação Trabalhista' },
    tribunal: 'TRT6',
    data_hora_ultima_atualizacao: '2025-05-01',
    grau: 'G1',
    data_ajuizamento: '2024-01-01',
    orgao_julgador: { codigo: 1, nome: '23ª Vara', codigo_municipio_ibge: null },
    assuntos: [{ codigo: 1, nome: 'Horas extras' }],
    analise: {
      id: 10,
      resumo: 'Resumo detalhado',
      tipo_ato_principal: 'sentenca',
      decisao: 'Decisão favorável',
      palavras_chave: [{ nome: 'horas_extras' }],
      status: 'sentenciado',
      desfecho: 'sentenca_procedente',
      resultado_reclamante: 'ganhou',
      valor_causa: '1000.00',
      custas_valor_total: '50.00',
    },
    similaridade: 0.91,
    movimentos: [
      {
        codigo: 2,
        nome: 'Conclusos para julgamento',
        data_hora: '2025-01-05T10:00:00',
        orgao_julgador: { codigo: 1, nome: '23ª Vara', codigo_municipio_ibge: null },
      },
      {
        codigo: 1,
        nome: 'Distribuído ao juízo',
        data_hora: '2024-01-02T10:00:00',
        orgao_julgador: { codigo: 1, nome: '23ª Vara', codigo_municipio_ibge: null },
      },
    ],
    em_andamento: false,
  }
}

async function mountPage(path = '/processos/0000256-48.2025.5.06.0171/G1') {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: { template: '<div />' } },
      { path: '/processos/:numeroProcesso/:grau', component: ProcessDetailPage },
      { path: '/:pathMatch(.*)*', component: { template: '<div />' } },
    ],
  })

  await router.push(path)
  await router.isReady()

  return mount(ProcessDetailPage, {
    global: {
      plugins: [
        router,
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

describe('ProcessDetailPage', () => {
  afterEach(() => {
    detalheSpy.mockReset()
  })

  it('carrega o detalhe do processo e ordena a timeline', async () => {
    detalheSpy.mockResolvedValueOnce(buildResponse())

    const wrapper = await mountPage()
    await flushPromises()

    expect(detalheSpy).toHaveBeenCalledWith('0000256-48.2025.5.06.0171', 'G1')
    expect(wrapper.text()).toContain('Resumo detalhado')
    expect(wrapper.text()).toContain('Finalizado')

    const text = wrapper.text()
    expect(text.indexOf('Distribuído ao juízo')).toBeLessThan(text.indexOf('Conclusos para julgamento'))
  })

  it('mostra estado inválido quando a rota não traz grau', async () => {
    const wrapper = await mountPage('/processos/0000256-48.2025.5.06.0171')
    await flushPromises()

    expect(wrapper.text()).toContain('Parâmetros inválidos')
  })
})