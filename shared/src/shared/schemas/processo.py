from typing import TypedDict


class OrgaoJulgadorDict(TypedDict, total=False):
    codigo: str
    nome: str


class MovimentoDict(TypedDict, total=False):
    codigo: int
    nome: str
    data_hora: str
    orgao_julgador: OrgaoJulgadorDict | None


class ProcessoDetalheDict(TypedDict, total=False):
    id: int
    numero_processo: str
    classe: str
    sistema: str
    formato: str
    tribunal: str
    data_hora_ultima_atualizacao: str
    grau: str
    timestamp: str
    data_ajuizamento: str
    movimentos: list[MovimentoDict]
    orgao_julgador: OrgaoJulgadorDict | None
    assuntos: list[str]

class ProcessoDict(TypedDict, total=False):
    id: int
    numero_processo: str
    classe: str
    sistema: str
    formato: str
    tribunal: str
    data_hora_ultima_atualizacao: str
    grau: str
    timestamp: str
    data_ajuizamento: str
    movimentos: list[MovimentoDict]
    orgao_julgador: OrgaoJulgadorDict | None
    assuntos: list[str]
