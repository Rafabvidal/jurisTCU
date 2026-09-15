"""Lógica de negócio do microserviço search-notifier.

Fluxo diário:
1. Lê as buscas salvas (e os dados do dono) direto do PostgreSQL via psycopg2.
2. Descomprime o campo ``last_results`` (zlib + JSON) para saber o que o usuário já viu.
3. Reexecuta a busca semântica na API e compara os ``numero_processo`` atuais.
4. Se houver processos novos, envia um e-mail HTML premium (ou loga, se SMTP off).
5. Persiste a nova baseline comprimida de volta no banco.
"""

from __future__ import annotations

import json
import smtplib
import zlib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import psycopg2
import requests
from shared.env_manager import EnviromentManager
from shared.logger import get_logger

logger = get_logger("search_notifier")
env = EnviromentManager()

# Quantidade de resultados considerados a cada checagem de busca semântica.
TOP_K = 10
# Tempo máximo (s) aguardando a API de busca semântica.
SEARCH_TIMEOUT_SECONDS = 60


# --------------------------------------------------------------------------- #
# Banco de dados
# --------------------------------------------------------------------------- #
def get_connection():
    """Abre conexão com o PostgreSQL usando as credenciais do ambiente."""
    return psycopg2.connect(
        host=env.get_postgres_host(),
        dbname=env.get_postgres_db(),
        user=env.get_postgres_user(),
        password=env.get_postgres_password(),
        port=env.get_postgres_port(),
    )


def fetch_saved_searches(conn) -> list[dict]:
    """Retorna as buscas salvas com o e-mail e nome do respectivo usuário."""
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT bs.id, bs.title, bs.query, bs.last_results, u.email, u.first_name
            FROM core_buscasalva AS bs
            JOIN auth_user AS u ON u.id = bs.user_id
            WHERE u.email <> ''
            ORDER BY bs.id
            """
        )
        rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "title": row[1],
            "query": row[2],
            "last_results": decompress_results(row[3]),
            "email": row[4],
            "name": row[5] or "",
        }
        for row in rows
    ]


def decompress_results(raw) -> list[str]:
    """Descomprime (zlib) e desserializa (JSON) o campo ``last_results``."""
    if not raw:
        return []
    try:
        decompressed = zlib.decompress(bytes(raw))
        value = json.loads(decompressed.decode("utf-8"))
        return value if isinstance(value, list) else []
    except (zlib.error, json.JSONDecodeError, ValueError) as exc:
        logger.warning("Falha ao descomprimir last_results, tratando como vazio: %s", exc)
        return []


def compress_results(numeros: list[str]) -> bytes:
    """Serializa (JSON) e comprime (zlib) a lista de numero_processo."""
    serialized = json.dumps(numeros, ensure_ascii=False)
    return zlib.compress(serialized.encode("utf-8"))


def update_last_results(conn, search_id: int, numeros: list[str]) -> None:
    """Grava a nova baseline comprimida na coluna bytea ``last_results``."""
    compressed = compress_results(numeros)
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE core_buscasalva SET last_results = %s WHERE id = %s",
            (psycopg2.Binary(compressed), search_id),
        )
    conn.commit()


# --------------------------------------------------------------------------- #
# Busca semântica
# --------------------------------------------------------------------------- #
def fetch_current_results(query: str) -> list[dict]:
    """Consulta a API de busca semântica e devolve a lista de itens (processos)."""
    url = f"{env.get_api_base_url().rstrip('/')}/api/processos/busca_semantica/"
    response = requests.post(
        url,
        json={"consulta": query, "top_k": TOP_K},
        timeout=SEARCH_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json().get("items", [])


def find_new_processos(current_items: list[dict], previous_numeros: list[str]) -> list[dict]:
    """Retorna apenas os itens cujo numero_processo ainda não foi visto."""
    previous = set(previous_numeros)
    return [item for item in current_items if item.get("numero_processo") not in previous]


# --------------------------------------------------------------------------- #
# E-mail
# --------------------------------------------------------------------------- #
def _format_similaridade(item: dict) -> str:
    similaridade = item.get("similaridade")
    if not isinstance(similaridade, (int, float)):
        return ""
    return f"{similaridade * 100:.0f}% de similaridade"


def _build_card(item: dict) -> str:
    numero = item.get("numero_processo", "—")
    analise = item.get("analise") or {}
    resumo = (analise.get("resumo") or "Resumo ainda não disponível.").strip()
    orgao = (item.get("orgao_julgador") or {}).get("nome", "")
    similaridade = _format_similaridade(item)

    meta_parts = [part for part in (orgao, similaridade) if part]
    meta = " · ".join(meta_parts)

    return f"""
      <div style="background:#ffffff;border:1px solid #dde3eb;border-radius:16px;
                  padding:20px;margin-bottom:14px;">
        <div style="font-weight:700;color:#002045;font-size:15px;">{numero}</div>
        <div style="color:#5d708f;font-size:12px;margin-top:4px;">{meta}</div>
        <p style="color:#314567;font-size:14px;line-height:1.5;margin:12px 0 0;">{resumo}</p>
      </div>
    """


def build_email_html(user_name: str, search_title: str, new_items: list[dict]) -> str:
    """Monta o corpo HTML premium do alerta de novos processos."""
    saudacao = f"Olá, {user_name}!" if user_name else "Olá!"
    cards = "".join(_build_card(item) for item in new_items)
    plural = "novos processos" if len(new_items) > 1 else "novo processo"

    return f"""<!DOCTYPE html>
<html lang="pt-br">
  <body style="margin:0;padding:24px;background:#f4f6fb;
               font-family:'Segoe UI',Arial,sans-serif;">
    <div style="max-width:560px;margin:0 auto;">
      <div style="background:#002045;border-radius:20px 20px 0 0;padding:28px 28px 22px;">
        <div style="color:#ffffff;font-size:20px;font-weight:800;
                    letter-spacing:-0.5px;">JusTRT6</div>
        <div style="color:#9db4d6;font-size:13px;margin-top:4px;">
          Alerta de busca salva
        </div>
      </div>
      <div style="background:#f6f9ff;border:1px solid #dde3eb;border-top:none;
                  border-radius:0 0 20px 20px;padding:28px;">
        <p style="color:#12233f;font-size:16px;margin:0 0 4px;font-weight:600;">
          {saudacao}
        </p>
        <p style="color:#5d708f;font-size:14px;line-height:1.5;margin:0 0 22px;">
          Encontramos <strong>{len(new_items)} {plural}</strong> para a sua busca salva
          <strong>“{search_title}”</strong>.
        </p>
        {cards}
        <p style="color:#90a0bb;font-size:12px;line-height:1.5;margin:22px 0 0;">
          Você recebeu este e-mail porque salvou esta busca no JusTRT6.
        </p>
      </div>
    </div>
  </body>
</html>"""


def send_email(recipient: str, subject: str, html_body: str) -> None:
    """Envia o e-mail via SMTP; se as credenciais não estiverem configuradas, apenas loga."""
    smtp_user = env.get_smtp_user()
    smtp_password = env.get_smtp_password()
    sender = env.get_smtp_sender()

    if not smtp_user or not smtp_password:
        logger.warning(
            "SMTP não configurado (SMTP_USER/SMTP_PASSWORD ausentes). "
            "E-mail NÃO enviado para %s. Assunto: %s",
            recipient,
            subject,
        )
        logger.info("Prévia do corpo que seria enviado:\n%s", html_body)
        return

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipient
    message.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP(env.get_smtp_host(), env.get_smtp_port(), timeout=30) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(sender, [recipient], message.as_string())

    logger.info("E-mail enviado para %s (assunto: %s)", recipient, subject)


# --------------------------------------------------------------------------- #
# Orquestração
# --------------------------------------------------------------------------- #
def process_saved_search(conn, search: dict) -> None:
    """Processa uma única busca salva: detecta novidades, notifica e atualiza baseline."""
    search_id = search["id"]
    title = search["title"]
    query = search["query"]
    previous_numeros = search["last_results"]

    try:
        current_items = fetch_current_results(query)
    except requests.RequestException as exc:
        logger.error("Busca #%s ('%s') falhou ao consultar a API: %s", search_id, title, exc)
        return

    current_numeros = [
        item["numero_processo"] for item in current_items if item.get("numero_processo")
    ]

    # Primeira execução para esta busca: apenas registra a baseline, sem notificar.
    if not previous_numeros:
        logger.info(
            "Busca #%s ('%s'): baseline inicial com %s processos. Sem notificação.",
            search_id,
            title,
            len(current_numeros),
        )
        update_last_results(conn, search_id, current_numeros)
        return

    new_items = find_new_processos(current_items, previous_numeros)

    if not new_items:
        logger.info("Busca #%s ('%s'): nenhum processo novo.", search_id, title)
        return

    logger.info(
        "Busca #%s ('%s'): %s processo(s) novo(s) para %s.",
        search_id,
        title,
        len(new_items),
        search["email"],
    )

    subject = f"JusTRT6 · {len(new_items)} novo(s) resultado(s) em “{title}”"
    html_body = build_email_html(search["name"], title, new_items)
    send_email(search["email"], subject, html_body)

    # Atualiza a baseline com todos os processos atuais (vistos + novos).
    update_last_results(conn, search_id, current_numeros)


def run() -> None:
    """Ponto de entrada da rotina diária."""
    logger.info("Iniciando verificação de buscas salvas...")

    conn = get_connection()
    try:
        searches = fetch_saved_searches(conn)
        logger.info("%s busca(s) salva(s) com e-mail para verificar.", len(searches))
        for search in searches:
            try:
                process_saved_search(conn, search)
            except Exception:
                logger.exception("Erro inesperado ao processar a busca #%s.", search.get("id"))
    finally:
        conn.close()

    logger.info("Verificação de buscas salvas concluída.")
