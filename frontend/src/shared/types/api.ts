export interface ClasseDTO {
  codigo: string
  nome: string
}

export interface OrgaoJulgadorDTO {
  id?: number
  codigo: number
  nome: string
  codigo_municipio_ibge: number | null
}

export interface AssuntoDTO {
  id?: number
  codigo: number
  nome: string
}

export interface PalavraChaveDTO {
  id?: number
  nome: string
}

export type TipoAtoPrincipal =
  | 'acordo_homologado'
  | 'sentenca'
  | 'acordao'
  | 'despacho'
  | 'outro'

export type StatusProcesso =
  | 'arquivado'
  | 'acordo_homologado'
  | 'sentenciado'
  | 'em_andamento'

export type Desfecho =
  | 'acordo_favoravel'
  | 'sentenca_procedente'
  | 'sentenca_parcialmente_procedente'
  | 'sentenca_improcedente'
  | 'extinta'
  | 'arquivado_sem_decisao'
  | 'outro'

export type ResultadoReclamante =
  | 'ganhou'
  | 'ganhou_parcial'
  | 'perdeu'
  | 'sem_decisao'

export interface AnaliseDTO {
  id: number
  resumo: string
  tipo_ato_principal: TipoAtoPrincipal
  decisao: string
  palavras_chave: PalavraChaveDTO[]
  status: StatusProcesso
  desfecho: Desfecho
  resultado_reclamante: ResultadoReclamante
  valor_causa: string
  custas_valor_total: string
}

export interface ProcessoDTO {
  id: number
  numero_processo: string
  classe: ClasseDTO
  tribunal: string
  data_hora_ultima_atualizacao: string
  grau: string
  data_ajuizamento: string
  orgao_julgador: OrgaoJulgadorDTO
  assuntos: AssuntoDTO[]
  analise: AnaliseDTO | null
  similaridade: number
}

export interface MovimentoDTO {
  codigo: number
  nome: string
  data_hora: string
  orgao_julgador: OrgaoJulgadorDTO | null
}

export interface ProcessoDetalheDTO extends ProcessoDTO {
  movimentos: MovimentoDTO[]
  em_andamento: boolean
}

export interface BuscaSemanticaPayload {
  consulta: string
  top_k: number
  metrica?: string
}

export interface BuscaSemanticaResponse {
  items: ProcessoDTO[]
}

export interface UserDTO {
  id: number
  name: string
  email: string
}

export interface AuthResponse {
  token: string
  user: UserDTO
}

export interface RegisterPayload {
  name: string
  email: string
  password: string
}

export interface LoginPayload {
  email: string
  password: string
}

export interface SavedSearchDTO {
  id: number
  title: string
  query: string
  created_at: string
  updated_at: string
}

/** Resposta paginada padrão do DRF (PageNumberPagination). */
export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}
