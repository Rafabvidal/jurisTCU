# Fluxo do Projeto

Este documento descreve o fluxo que ja esta implementado no codigo e o que ainda falta implementar para o projeto chegar ao fluxo completo de analise e busca semantica.

Observacao: este texto reflete o estado atual do repositorio, nao a documentacao idealizada.

## Visao geral

Hoje o projeto ja possui uma base funcional para:

- consultar processos no DataJud
- normalizar e persistir esses processos na API Django
- identificar processos sem PDF no armazenamento
- disparar um worker de scraping para baixar a integra do PJe
- salvar o arquivo no MinIO
- prototipar uma analise com LLM a partir de um arquivo local

O que ainda nao existe de ponta a ponta:

- encadeamento automatico do scraper para o worker de LLM
- endpoint da API para receber a analise gerada pela LLM
- indexacao vetorial
- busca semantica real
- integracao do frontend com a API de busca

## Arquitetura atual por modulo

### 1. `apps/ingestion`

Responsabilidade atual:

- consultar dados do DataJud
- mapear o payload para o formato esperado pela API
- enviar lotes para deduplicacao
- opcionalmente disparar o scraping via Celery

Arquivos principais:

- `apps/ingestion/src/ingestion/providers.py`
- `apps/ingestion/src/ingestion/main.py`
- `apps/ingestion/src/ingestion/submitter.py`

### 2. `apps/api`

Responsabilidade atual:

- persistir processos e relacionamentos
- deduplicar novos lotes recebidos do DataJud
- verificar quais processos ainda nao possuem PDF no MinIO

Arquivos principais:

- `apps/api/api/urls.py`
- `apps/api/core/views.py`
- `apps/api/core/services.py`
- `apps/api/core/models/`
- `apps/api/core/serializers/`

### 3. `apps/worker-scrapper`

Responsabilidade atual:

- resolver captcha do PJe
- obter o token de acesso
- baixar a integra do processo
- enviar o arquivo para o MinIO

Arquivos principais:

- `apps/worker-scrapper/pje_scraper/pipeline.py`
- `apps/worker-scrapper/pje_scraper/scraper.py`
- `apps/worker-scrapper/pje_scraper/worker.py`

### 4. `apps/worker-llm`

Responsabilidade atual:

- prototipar a extracao estruturada de informacoes juridicas a partir de um arquivo local
- gerar um objeto no formato `ProcessoAnalise`

Arquivos principais:

- `apps/worker-llm/main.py`
- `shared/src/shared/schemas/resumo_ia.py`

Limite atual:

- nao e uma task Celery integrada ao fluxo real
- nao baixa o PDF do MinIO
- nao atualiza a API Django

### 5. `shared`

Responsabilidade atual:

- cliente Celery compartilhado
- cliente MinIO compartilhado
- schemas Pydantic compartilhados

Arquivos principais:

- `shared/src/shared/celery_client.py`
- `shared/src/shared/s3_client.py`
- `shared/src/shared/schemas/`

### 6. `frontend`

Responsabilidade atual:

- exibir a interface da busca
- simular resultados e insights com dados mockados

Arquivos principais:

- `frontend/src/pages/HomePage/composables/useHomeSearch.ts`
- `frontend/src/pages/HomePage/utils/searchMatching.ts`
- `frontend/src/shared/constants/mockCases.ts`

Limite atual:

- nao faz chamadas reais para a API
- nao consome busca semantica

## Fluxo que ja esta implementado

### Etapa 1. Consulta ao DataJud

O fluxo comeca no pacote de ingestao.

1. `apps/ingestion/src/ingestion/main.py` define a lista de topicos juridicos.
2. Para cada topico, o provider consulta a API do DataJud ou um arquivo local.
3. A resposta e validada com schema Pydantic.
4. O payload e normalizado para o formato esperado pela API Django.

Saida desta etapa:

- uma lista de processos em formato padronizado

### Etapa 2. Envio para a API Django

Depois de normalizar os dados:

1. `ProcessSubmitter` envia o lote para `POST /api/processos/deduplicar/`.
2. A view `ProcessoViewset.deduplicar` valida o payload.
3. O service `filtrar_processos_faltantes` remove duplicatas do request e do banco.
4. Os processos novos sao persistidos com serializer e relacionamentos.

Saida desta etapa:

- processos novos salvos no banco relacional
- resposta com os processos efetivamente criados

### Etapa 3. Descoberta de processos sem PDF

Ja existe um fluxo para buscar pendencias de PDF.

1. O ingestor pode rodar em modo `pending_pdf`.
2. Nesse modo ele chama `GET /api/processos/nao_possuem_pdf/`.
3. A API consulta processos sem `pdf_url` e verifica se o objeto existe no MinIO.
4. Se nao existir no bucket, o processo volta como pendente.

Saida desta etapa:

- lista de processos que ainda precisam de scraping

### Etapa 4. Disparo do worker de scraping

Quando o ingestor esta configurado para disparar processamento:

1. `apps/ingestion/src/ingestion/main.py` chama `run_pipeline.delay(...)`.
2. O Celery envia a task para o worker do scraper usando RabbitMQ.

Saida desta etapa:

- task enfileirada para baixar a integra do processo

### Etapa 5. Scraping do PJe

No worker de scraping:

1. `PjePipeline.resolve(...)` resolve captcha e obtem `tokenCaptcha`.
2. `fetch_with_token(...)` baixa a integra do processo.
3. O worker cria ou reutiliza o bucket `pje-documents`.
4. O arquivo e enviado para o MinIO com nome baseado em numero do processo e grau.

Saida desta etapa:

- PDF ou retorno da integra salvo no MinIO

### Etapa 6. Analise por LLM em modo prototipo

O projeto ja possui uma prova de conceito de analise estruturada.

1. `apps/worker-llm/main.py` le um arquivo local de exemplo.
2. O texto e enviado para um modelo via interface compativel com OpenAI.
3. A resposta e validada contra `ProcessoAnalise`.
4. O resultado e salvo em arquivo JSON local.

Saida desta etapa:

- JSON estruturado com resumo, decisao, palavras-chave e classificacoes

Limite:

- essa etapa ainda nao esta conectada ao PDF salvo no MinIO nem ao Django

### Etapa 7. Frontend de busca em modo mock

O frontend ja possui a tela de busca, mas ainda sem backend real.

1. O usuario digita uma consulta.
2. O composable `useHomeSearch` ativa o estado de busca.
3. Os resultados sao montados a partir de `MOCK_CASES`.
4. O ranking final e ajustado por palavras-chave locais em `searchMatching.ts`.

Saida desta etapa:

- lista visual de processos simulados
- painel de insights tambem mockado

## O que falta implementar

### 1. Atualizacao do processo apos o scraping

Hoje o scraper salva o arquivo no MinIO, mas nao fecha o ciclo com a API.

Falta:

- atualizar o processo com referencia ao PDF salvo
- registrar de forma explicita que o documento foi obtido com sucesso

### 2. Worker de LLM integrado ao fluxo real

Hoje o `worker-llm` e um script manual.

Falta:

- transformar o worker em task Celery
- receber `numero`, `grau`, `bucket` e `object_name`
- baixar o PDF do MinIO
- extrair texto do PDF real
- gerar `ProcessoAnalise`

### 3. Endpoint para salvar a analise no Django

Hoje a API aceita criacao de `analise` junto com o processo no endpoint de deduplicacao, mas nao existe um endpoint dedicado para a etapa posterior de analise.

Falta:

- criar algo como `POST /api/processos/adicionar-analise/`
- localizar o processo correto
- criar ou atualizar `Analise`
- salvar palavras-chave e campos derivados

### 4. Encadeamento entre scraper e LLM

Hoje o fluxo para no MinIO.

Falta:

- ao final do scraping, disparar a task do `worker-llm`
- garantir retry independente entre scraping e analise

### 5. Indexacao vetorial

Hoje nao existe camada de embeddings nem base vetorial.

Falta:

- gerar embedding de cada processo analisado
- armazenar vetor e metadados em um banco vetorial
- manter estrategia de reindexacao quando a analise mudar

### 6. Busca semantica real

Hoje nao existe endpoint para consulta por similaridade.

Falta:

- criar endpoint como `POST /api/processos/busca-semantica/`
- transformar a consulta do usuario em embedding
- buscar os vetores mais proximos
- hidratar os resultados com os dados do Django
- devolver `similaridade` para o frontend

### 7. Integracao do frontend com o backend

Hoje a interface e visualmente pronta, mas usa dados locais.

Falta:

- remover dependencia de `MOCK_CASES` na Home
- chamar a API de busca
- mapear o payload da API para os tipos do frontend
- renderizar resultados reais

## Resumo do estado atual

### Ja implementado

- consulta ao DataJud
- normalizacao do payload
- persistencia e deduplicacao de processos
- consulta de pendencias de PDF
- task Celery para scraping
- scraping do PJe com captcha
- armazenamento do PDF no MinIO
- prova de conceito de analise com LLM
- frontend com interface de busca pronta

### Faltando para o fluxo completo

- callback do scraping para a API
- worker de LLM integrado ao fluxo real
- endpoint para adicionar analise ao processo
- embeddings e indexacao vetorial
- endpoint de busca semantica
- frontend consumindo dados reais

## Fluxo alvo resumido

O fluxo alvo do projeto fica assim:

1. Ingestao consulta DataJud.
2. API deduplica e persiste processos.
3. Ingestor ou job localiza processos sem PDF.
4. Worker de scraping baixa a integra e salva no MinIO.
5. Worker de LLM baixa o PDF, extrai e estrutura a analise.
6. API salva a analise e indexa o processo no banco vetorial.
7. Frontend consulta a API de busca semantica.
8. O usuario recebe processos similares com score e insights.
