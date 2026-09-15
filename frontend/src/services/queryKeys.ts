import { QUERY_KEYS } from '@/shared/constants/api'

export const queryKeys = {
  buscaSemantica: (consulta: string, topK: number, metrica?: string) =>
    [QUERY_KEYS.buscaSemantica, { consulta, topK, metrica }] as const,
  naoPossuemAnalise: () => [QUERY_KEYS.naoPossuemAnalise] as const,
  naoPossuemPdf: () => [QUERY_KEYS.naoPossuemPdf] as const,
  processoDetalhe: (numeroProcesso: string, grau: string) =>
    [QUERY_KEYS.processoDetalhe, { numeroProcesso, grau }] as const,
  savedSearches: () => [QUERY_KEYS.savedSearches] as const,
}
