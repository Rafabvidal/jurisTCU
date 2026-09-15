from datetime import date

DEDUPLICAR_ENDPOINT = "/api/processos/deduplicar/"
NAO_POSSUEM_PDF_ENDPOINT = "/api/processos/nao_possuem_pdf/"
NAO_POSSUEM_ANALISE_ENDPOINT = "/api/processos/nao_possuem_analise/"
DETALHE_PROCESSO_ENDPOINT = "/api/processos/detalhe/"

PROCESSO_NUMERO_1 = "00002564820255060171"
PROCESSO_NUMERO_2 = "00002564820255060172"
PROCESSO_NUMERO_3 = "00002564820255060173"

TRIBUNAL_TRT6 = "TRT6"
GRAU_G1 = "G1"

DATA_ANTIGA = date(2024, 12, 1)
DATA_BASE = date(2025, 1, 1)
DATA_NOVA = date(2025, 1, 15)

RESUMO_RESPONSE_KEYS = {"numero_processo", "grau"}
