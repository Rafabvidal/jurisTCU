# Ingestion

Este pacote consulta dados de processos, normaliza o payload e envia lotes para a API em /api/processos/deduplicar/.

## Executar ingest local

```bash
uv run ingest
```

## Habilitar log detalhado de erro da API

No ambiente local, use a variavel LOG_ERRORS para incluir status HTTP e corpo da resposta quando houver erro de envio:

```bash
LOG_ERRORS=true uv run ingest
```

Com LOG_ERRORS desabilitado, o submitter mantém log resumido.

## Rodar testes de integracao do fluxo de ingestao

A partir de apps/api:

```bash
uv run pytest core/tests/integration/test_ingestion_pipeline_integration.py
```

Esses testes usam fixture derivada de apps/api/data/dataJud.json e exercitam o fluxo:

1. leitura com FileDataProvider
2. transformacao com mapear_processos
3. envio para endpoint real do Django em ambiente de teste
