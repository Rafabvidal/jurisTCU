from typing import TypedDict


class ClasseDict:
    codigo: str
    nome: str

class ProcessoDict(TypedDict):
    numero_processo: str
    classe: ClasseDict
    tribunal: str
    data_hora_ultima_atualizacao: str
    grau: str
    data_ajuizamento: str
    orgao_julgador: str
    assuntos: list
    analise: str
