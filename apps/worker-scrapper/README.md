# pje-scraper

Automação do fluxo de consulta processual no **PJe TRT-6** (`pje.trt6.jus.br/consultaprocessual`):  
busca processo → seleciona grau → resolve captcha via `ddddocr` → retorna `tokenCaptcha` pronto para uso na API.

## Pré-requisitos

- Python 3.11+
- Chromium (instalado via Playwright)

## Instalação

```bash
# A partir da raiz do repositório
pip install -e captcha_service/

# Instala o browser Chromium para o Playwright
playwright install chromium
```

## Uso — linha de comando

Após instalar o pacote, o comando `pje-scraper` fica disponível globalmente:

```bash
# Sintaxe
pje-scraper <numero_processo> [grau] [--no-headless]

# Exemplos
pje-scraper 0000573-11.2025.5.06.0021
pje-scraper 0000573-11.2025.5.06.0021 2
pje-scraper 0000573-11.2025.5.06.0021 1 --no-headless   # abre o navegador visível
```

Saída esperada:
```
processo_id  : 123456
grau         : 1
captcha_text : 3n3D
tokenDesafio : abc123...
tokenCaptcha : xyz789...
```

## Uso — script principal

```bash
# Via main.py (captura o PDF final interceptando o fetch do navegador)
python captcha_service/main.py 0000573-11.2025.5.06.0021
python captcha_service/main.py 0000573-11.2025.5.06.0021 1 --no-headless
```

## Uso — Python

```python
from pje_scraper import PjePipeline

pipeline = PjePipeline()                          # headless=True por padrão
session = pipeline.resolve("0000573-11.2025.5.06.0021", grau="1")

print(session.token_captcha)   # token pronto para a API

# Fluxo recomendado: capturar o PDF no response que o navegador já faz
capture = pipeline.resolve_and_capture_pdf("0000573-11.2025.5.06.0021", grau="1")
path = pipeline.save_captured_pdf(capture)
print(path)

# Opcional: buscar documentos do processo diretamente
resp = pipeline.fetch_with_token(session)
print(resp.json())
```

### `CaptchaSession` — campos retornados

| Campo | Descrição |
|---|---|
| `numero_processo` | Número CNJ do processo |
| `grau` | `"1"` ou `"2"` |
| `processo_id` | ID interno usado na API do PJe |
| `token_desafio` | Token do desafio captcha |
| `token_captcha` | Token resultante após resolver o captcha |
| `captcha_text` | Texto reconhecido pelo OCR |

## Estrutura do pacote

```
captcha_service/
├── pje_scraper/
│   ├── captcha.py    # CaptchaSolver: wrapper do ddddocr (OCR local)
│   ├── scraper.py    # PjeScraper: automação Playwright
│   ├── pipeline.py   # PjePipeline: orquestra tudo + entry point CLI
│   └── models.py     # Dataclasses: CaptchaSession, ProcessInfo, GrauInfo
├── main.py           # Script principal: resolve captcha + busca documentos
└── pyproject.toml
```

## Páginas de referência

As capturas HTML em `pagina inicial/`, `pagina com captcha/` e `mais de um grau trt6/` documentam a estrutura real das páginas usadas na automação.
