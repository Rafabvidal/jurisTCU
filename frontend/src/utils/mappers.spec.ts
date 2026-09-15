import { describe, expect, it } from 'vitest'

import type { ProcessoDTO } from '@/shared/types/api'

import { mapProcessoDTOToProcessCase } from './mappers'

function buildDTO(overrides: Partial<ProcessoDTO> = {}): ProcessoDTO {
  return {
    id: 1,
    numero_processo: '00002564820255060171',
    classe: { codigo: '1800', nome: 'Reclamação' },
    tribunal: 'TRT6',
    data_hora_ultima_atualizacao: '2025-01-20',
    grau: 'G1',
    data_ajuizamento: '2024-01-20',
    orgao_julgador: {
      id: 1,
      codigo: 3210,
      nome: '5ª JCJ Recife',
      codigo_municipio_ibge: 2611606,
    },
    assuntos: [{ id: 1, codigo: 2001, nome: 'Direito do Trabalho' }],
    analise: {
      id: 32,
      resumo: 'Resumo do caso',
      tipo_ato_principal: 'sentenca',
      decisao: 'Decisão procedente',
      palavras_chave: [
        { id: 1, nome: 'horas_extras' },
        { id: 2, nome: 'jornada' },
      ],
      status: 'sentenciado',
      desfecho: 'sentenca_procedente',
      resultado_reclamante: 'ganhou',
      valor_causa: '1234.56',
      custas_valor_total: '99.99',
    },
    similaridade: 0.92,
    ...overrides,
  }
}

describe('mapProcessoDTOToProcessCase', () => {
  it('converte string decimal para number e achata palavras-chave', () => {
    const result = mapProcessoDTOToProcessCase(buildDTO())

    expect(result.valorCausa).toBe(1234.56)
    expect(result.custasValorTotal).toBe(99.99)
    expect(result.palavrasChave).toEqual(['horas_extras', 'jornada'])
  })

  it('extrai nomes de classe e órgão julgador', () => {
    const result = mapProcessoDTOToProcessCase(buildDTO())

    expect(result.classeNome).toBe('Reclamação')
    expect(result.orgaoJulgadorNome).toBe('5ª JCJ Recife')
  })

  it('calcula tempo de tramitação em meses', () => {
    const result = mapProcessoDTOToProcessCase(buildDTO())
    expect(result.tempoTramitacaoMeses).toBeGreaterThanOrEqual(11)
    expect(result.tempoTramitacaoMeses).toBeLessThanOrEqual(13)
  })

  it('lida com analise nula sem quebrar', () => {
    const result = mapProcessoDTOToProcessCase(buildDTO({ analise: null }))

    expect(result.valorCausa).toBe(0)
    expect(result.palavrasChave).toEqual([])
    expect(result.statusProcesso).toBeNull()
    expect(result.desfecho).toBeNull()
    expect(result.resultadoReclamante).toBeNull()
  })

  it('propaga similaridade e número do processo', () => {
    const result = mapProcessoDTOToProcessCase(buildDTO())
    expect(result.similaridade).toBe(0.92)
    expect(result.numeroProcesso).toBe('00002564820255060171')
  })
})
