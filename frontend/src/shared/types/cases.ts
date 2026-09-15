import type {
    Desfecho,
    ResultadoReclamante,
    StatusProcesso,
} from './api'

export interface ProcessCase {
  id: number
  numeroProcesso: string
  grau: string
  tribunal: string
  classeNome: string
  orgaoJulgadorNome: string
  dataAjuizamento: string
  dataUltimaAtualizacao: string
  tempoTramitacaoMeses: number
  resumoCausa: string
  decisaoResumo: string
  palavrasChave: string[]
  statusProcesso: StatusProcesso | null
  desfecho: Desfecho | null
  resultadoReclamante: ResultadoReclamante | null
  valorCausa: number
  custasValorTotal: number
  similaridade: number
}

export interface InsightKpis {
  totalCases: number
  valorMedio: number
  valorTotal: number
  valorMaximo: number
  taxaProcedencia: number
  taxaGanhoReclamante: number
  tempoMedioMeses: number
  palavrasChavesRelevantes: string[]
}

export interface ChartSeries {
  labels: string[]
  values: number[]
}

export interface ValorRadial {
  atual: number
  maximo: number
  percentual: number
}

export interface HomeInsights {
  kpis: InsightKpis
  desfechoSeries: ChartSeries
  statusSeries: ChartSeries
  resultadoSeries: ChartSeries
  valorRadial: ValorRadial
}
