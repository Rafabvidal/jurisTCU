# Plano de Otimização e Padronização Docker + uv

## 1. Contexto e Diagnóstico

### Situação Anterior
Anteriormente, todos os 5 serviços (`api`, `ingestion`, `worker-llm`, `worker-scrapper`, `search-notifier`) utilizavam um padrão manual e ineficiente de build no Docker:
1. `COPY` de todo o código fonte antes de instalar dependências.
2. Extração via script bash (`uv export`, `awk`, `grep`).
3. Compilação manual de wheels com `uv build`.
4. Instalação manual com `uv pip install --system`.

### Gargalos Identificados
- **Invalidação prematura de cache do Docker**: Qualquer edição em um arquivo `.py` de qualquer app invalidava todo o cache e forçava a reconstrução completa das dependências.
- **Falta de cache do uv**: A ausência de `--mount=type=cache,target=/root/.cache/uv` descartava o cache a cada execução de container.
- **Acoplamento de dependências pesadas em `shared`**: `sentence-transformers` e PyTorch estavam listados como dependências mandatórias no `shared/pyproject.toml`, forçando o download de centenas de megabytes em todos os containers, mesmo nos que só precisavam de schemas Pydantic ou Celery client.

---

## 2. Decisões Arquiteturais

1. **Estrutura de Monorepo com Workspaces do uv**:
   - Mantido o modelo oficial de workspace (`[tool.uv.workspace]`), pois cada app mantém seu ciclo de vida, entrypoints (`project.scripts`) e dependências isoladas.
   - Mantido `shared/` na raiz como biblioteca reutilizável interna.

2. **Isolamento de dependências no `shared`**:
   - `sentence-transformers` foi movido para o extra opcional:
     ```toml
     [project.optional-dependencies]
     embeddings = ["sentence-transformers>=2.2.0"]
     ```
   - Apenas a `api` instala `shared[embeddings]`, poupando tempo e espaço em disco em todos os demais serviços.

3. **Padrão Multi-Stage Docker oficial Astral uv**:
   - **Stage 1 (`builder`)**:
     - Configura `UV_COMPILE_BYTECODE=1` e `UV_LINK_MODE=copy`.
     - Copia apenas manifestos (`pyproject.toml` raiz, `uv.lock`, e os `pyproject.toml` dos membros relevantes).
     - Executa `uv sync --frozen --no-install-workspace --package <app>` com cache mount do uv (`--mount=type=cache,target=/root/.cache/uv`).
     - Copia o código-fonte da aplicação e do `shared`.
     - Executa `uv sync --frozen --package <app>` para instalar o código local.
   - **Stage 2 (`runtime`)**:
     - Imagem limpa `python:3.13-slim` (com dependências de SO específicas caso necessário, ex: Playwright no scrapper ou JRE no worker-llm).
     - Copia apenas o ambiente virtual `/app/.venv` e o código.
     - Executa através de `ENV PATH="/app/.venv/bin:$PATH"`.

---

## 3. Roteiro de Execução e Status

- [x] **Fase 1**: Extração de dependência opcional no `shared/pyproject.toml` e declaração de `shared[embeddings]` no `apps/api/pyproject.toml`.
- [x] **Fase 2**: Atualização do `uv.lock` via `uv lock`.
- [x] **Fase 3**: Otimização do `apps/api/Dockerfile`.
- [x] **Fase 4**: Otimização do `apps/ingestion/Dockerfile`.
- [x] **Fase 5**: Otimização do `apps/worker-llm/Dockerfile`.
- [x] **Fase 6**: Otimização do `apps/worker-scrapper/Dockerfile`.
- [x] **Fase 7**: Otimização do `apps/search-notifier/Dockerfile`.
- [x] **Fase 8**: Validação de build das imagens, medições e testes de execução.

---

## 4. Métricas, Tempos de Build e Logs de Execução

### Passo 1: Resolução do uv Lock
- **Comando**: `uv lock`
- **Tempo**: 28.46s
- **Resultado**: Resolvidos 290 pacotes no lockfile da raiz com o extra `[embeddings]` isolado.

### Passo 2: Validação e Aprendizado de Build (`apps/api`)
- **Problema encontrado inicialmente com `--no-install-project`**:
  O uv tentava compilar o workspace member `shared` em modo editável via build backend do setuptools (`setuptools.build_meta.build_editable`), mas o diretório `shared/src` ainda não havia sido copiado para o container, gerando o erro:
  ```text
  error: error in 'egg_base' option: 'src' does not exist or is not a directory
  hint: `shared` was included because `api` (v0.1.0) depends on `shared`
  ```
- **Solução definitiva da Astral uv**:
  Usar `--no-install-workspace`, que diz ao uv para ignorar todos os membros locais do workspace no primeiro stage e instalar apenas os pacotes de terceiros no cache mount.
- **Resultado do Build (`apps/api:test`)**:
  - `uv sync --frozen --package api` para instalar o código local: **2.9s**
  - Teste de container (`docker run --rm --entrypoint python juristcu-api:test -c "import django, shared; print('Django & Shared OK')"`):
    ```text
    Django & Shared OK
    ```
  - Rebuild com cache de camadas: **100% dos pacotes de terceiros reutilizados sem re-download**.

### Passo 3: Validação do Microsserviço Enxuto (`apps/search-notifier`)
Com a separação de `sentence-transformers` do `shared`:
- **Comando**: `docker build -t juristcu-search-notifier:test -f apps/search-notifier/Dockerfile .`
- **Tempo Total**: **11.2s**
- **Etapas e durações**:
  - Download do supercronic: 3.0s
  - `uv sync --frozen --no-install-workspace --package search-notifier` (via cache mount): **3.4s**
  - `uv sync --frozen --package search-notifier` (instalação local): **2.1s**
  - Criação e cópia do runtime: **3.3s**
- **Log de execução do container**:
  - Comando: `docker run --rm --entrypoint python juristcu-search-notifier:test -c "import shared, search_notifier; print('search-notifier & shared OK')"`
  - Saída:
    ```text
    search-notifier & shared OK
    ```

---

## 5. Comparativo de Performance

| Cenário | Padrão Anterior | Novo Padrão (uv Multi-stage + Cache) |
|---|---|---|
| **Build de serviço leve (ex: `search-notifier`)** | ~3 a 5 min (baixando PyTorch/sentence-transformers) | **11.2 segundos** |
| **Rebuild após alterar código Python (.py)** | Rebuild total + reinstalação do zero | **Instantâneo (camada de código copiada em < 3s)** |
| **Download de wheels entre containers** | Descartado a cada build | **Reutilizado via `--mount=type=cache,target=/root/.cache/uv`** |
| **Tamanho e segurança da imagem final** | Binário do uv, compiladores e scripts no runtime | **Apenas Python slim + `.venv` de produção** |
