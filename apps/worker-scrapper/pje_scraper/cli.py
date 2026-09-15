import json
import sys
from pathlib import Path

from pje_scraper import PjePipeline

DOCUMENTS_DIR = Path(__file__).resolve().parent / "documents"

def main():
    numero = sys.argv[1] if len(sys.argv) > 1 else "0000573-11.2025.5.06.0021"
    grau = sys.argv[2] if len(sys.argv) > 2 else "1"
    headless = "--no-headless" not in sys.argv

    print(f"[*] Buscando processo: {numero} | Grau: {grau}")

    pipeline = PjePipeline(headless=headless)

    try:
        session = pipeline.resolve(numero, grau=grau)
    except Exception as e:
        print(f"[!] Erro: {e}")
        sys.exit(1)

    print("\n[✓] Captcha resolvido!")
    print(f"    Processo ID  : {session.processo_id}")
    print(f"    Captcha texto: {session.captcha_text}")
    print(f"    tokenDesafio : {session.token_desafio}")
    print(f"    tokenCaptcha : {session.token_captcha}")

    print("\n[*] Baixando íntegra completa via endpoint /processos/{id}/integra...")
    http_download_ok = False
    try:
        resp = pipeline.fetch_with_token(session)
        content_type = resp.headers.get("content-type", "")
        print(f"    Status       : {resp.status_code}")
        print(f"    Content-Type : {content_type}")
        if "application/json" in content_type:
            preview = json.dumps(resp.json(), indent=2, ensure_ascii=False)[:500]
            print(f"    Body (JSON)  : {preview}")
        elif "application/pdf" in content_type:
            print("    Body (raw)   : <PDF binary omitted>")
        else:
            print(f"    Body (raw)   : {resp.text[:300]}")
        out = pipeline.save_http_response(session, resp)
        print(f"    Arquivo salvo: {out}")
        http_download_ok = resp.status_code == 200
        # Trigger deduplication after a successful download
        from ..deduplication import deduplicate_processos
        deduplicate_processos.delay()
    except Exception as e:
        print(f"[!] Erro ao baixar íntegra via HTTP: {e}")

    if http_download_ok:
        return

    print("\n[*] Fallback opcional: capturar o retorno da íntegra direto do navegador...")
    try:
        capture = pipeline.resolve_and_capture_document(numero, grau=grau)
        out = pipeline.save_captured_document(capture)
        print(f"    Content-Type : {capture.content_type}")
        print(f"    URL integra  : {capture.pdf_url}")
        print(f"    Arquivo salvo: {out}")
    except Exception as e:
        print(f"    [!] Fallback falhou (sem impactar o download HTTP): {e}")


if __name__ == "__main__":
    main()
