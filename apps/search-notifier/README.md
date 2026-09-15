# search-notifier

Microserviço cron que verifica diariamente se as buscas salvas dos usuários têm
novos resultados na busca semântica e envia um e-mail de alerta.

## Como funciona

1. Lê as buscas salvas e os dados do usuário direto do PostgreSQL (`psycopg2`).
2. Descomprime o campo `last_results` (`zlib` + JSON) para saber o que já foi visto.
3. Reexecuta a busca em `POST /api/processos/busca_semantica/`.
4. Compara os `numero_processo` atuais com a baseline anterior.
5. Havendo novidades, envia um e-mail HTML via `smtplib` (ou apenas loga, se o SMTP
   não estiver configurado) e atualiza a baseline comprimida no banco.

## Execução manual

```bash
docker compose run --rm search-notifier search-notifier
```

## Variáveis de ambiente

- `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`
- `API_BASE_URL` (ex.: `http://api:8000`)
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_SENDER`

Sem `SMTP_USER`/`SMTP_PASSWORD`, o serviço loga o que seria enviado sem quebrar.
