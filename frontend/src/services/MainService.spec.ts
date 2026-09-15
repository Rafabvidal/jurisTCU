import { afterEach, describe, expect, it, vi } from 'vitest'

import { API_ENDPOINTS } from '@/shared/constants/api'

const mockPost = vi.fn()
const mockGet = vi.fn()

vi.mock('./httpClient', () => ({
  httpClient: {
    post: (...args: unknown[]) => mockPost(...args),
    get: (...args: unknown[]) => mockGet(...args),
  },
}))

import { MainService } from './MainService'

describe('MainService', () => {
  afterEach(() => {
    mockPost.mockReset()
    mockGet.mockReset()
  })

  it('chama o endpoint correto de busca semântica com o payload exato', async () => {
    mockPost.mockResolvedValueOnce({ data: { items: [] } })

    const response = await MainService.buscaSemantica({
      consulta: 'horas extras',
      top_k: 10,
    })

    expect(mockPost).toHaveBeenCalledWith(
      API_ENDPOINTS.buscaSemantica,
      { consulta: 'horas extras', top_k: 10 },
    )
    expect(response).toEqual({ items: [] })
  })

  it('lista processos sem análise via GET no endpoint correto', async () => {
    mockGet.mockResolvedValueOnce({
      data: [{ numero_processo: 'ABC', grau: '1' }],
    })

    const result = await MainService.listarProcessosSemAnalise()

    expect(mockGet).toHaveBeenCalledWith(API_ENDPOINTS.naoPossuemAnalise)
    expect(result).toHaveLength(1)
    expect(result[0]?.numero_processo).toBe('ABC')
  })

  it('lista processos sem PDF via GET no endpoint correto', async () => {
    mockGet.mockResolvedValueOnce({ data: [] })

    await MainService.listarProcessosSemPdf()

    expect(mockGet).toHaveBeenCalledWith(API_ENDPOINTS.naoPossuemPdf)
  })

  it('busca o detalhe do processo via GET com query params', async () => {
    mockGet.mockResolvedValueOnce({
      data: {
        id: 1,
        numero_processo: '0001',
        classe: { codigo: '1', nome: 'Classe' },
        tribunal: 'TRT6',
        data_hora_ultima_atualizacao: '2025-01-01',
        grau: 'G1',
        data_ajuizamento: '2024-01-01',
        orgao_julgador: { codigo: 1, nome: 'Vara', codigo_municipio_ibge: null },
        assuntos: [],
        analise: null,
        similaridade: 0,
        movimentos: [],
        em_andamento: true,
      },
    })

    const result = await MainService.obterProcessoDetalhe('0001', 'G1')

    expect(mockGet).toHaveBeenCalledWith(
      API_ENDPOINTS.processoDetalhe,
      {
        params: {
          numero_processo: '0001',
          grau: 'G1',
        },
      },
    )
    expect(result.em_andamento).toBe(true)
  })
})
