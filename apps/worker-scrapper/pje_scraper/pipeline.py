"""
Pipeline de alto nível: dado um número de processo, retorna o tokenCaptcha
pronto para uso em requisições à API do PJe.
"""

from pathlib import Path

import httpx

from .captcha import CaptchaSolver
from .models import CaptchaPdfCapture, CaptchaSession
from .scraper import PjeScraper

PJE_PROCESSOS_API_BASE = "https://pje.trt6.jus.br/pje-consulta-api/api/processos"
DOCUMENTS_DIR = Path(__file__).resolve().parent.parent / "documents"


class PjePipeline:
    """
    Orquestra: busca → seleção de grau → resolução de captcha → tokenCaptcha.

    Usage:
        from pje_scraper import PjePipeline
        pipeline = PjePipeline()
        session = pipeline.resolve("0000573-11.2025.5.06.0021", grau="1")
        docs = pipeline.fetch_with_token(session)
    """

    def __init__(self, headless: bool = True, timeout_ms: int = 30_000):
        solver = CaptchaSolver()
        self.scraper = PjeScraper(solver, headless=headless, timeout_ms=timeout_ms)

    def resolve(self, numero_processo: str, grau: str = "1") -> CaptchaSession:
        """
        Executa o pipeline completo e retorna um CaptchaSession com tokenCaptcha.

        Raises:
            RuntimeError: Se o tokenCaptcha não foi obtido.
            TimeoutError: Se a página demorou demais para responder.
        """
        return self.scraper.get_token_captcha(numero_processo, grau=grau)

    def resolve_and_capture_document(
        self,
        numero_processo: str,
        grau: str = "1",
        pdf_wait_ms: int = 20_000,
    ) -> CaptchaPdfCapture:
        """
        Executa o fluxo completo no navegador e captura o retorno final da íntegra.
        """
        return self.scraper.get_pdf_from_browser_flow(
            numero_processo,
            grau=grau,
            pdf_wait_ms=pdf_wait_ms,
        )

    def save_captured_document(
        self,
        capture: CaptchaPdfCapture,
        output_path: str | Path | None = None,
    ) -> Path:
        """Salva em disco o retorno capturado no fluxo de navegador."""
        if output_path is None:
            filename = (
                f"{capture.session.numero_processo.replace('/', '_')}_integra"
                f"{self._extension_for_content_type(capture.content_type)}"
            )
            out = DOCUMENTS_DIR / filename
        else:
            out = Path(output_path)

        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(capture.pdf_bytes)
        return out

    def save_captured_pdf(
        self,
        capture: CaptchaPdfCapture,
        output_path: str | Path | None = None,
    ) -> Path:
        """Compatibilidade retroativa para o nome antigo do método."""
        return self.save_captured_document(capture, output_path=output_path)

    def save_http_response(
        self,
        session: CaptchaSession,
        response: httpx.Response,
        output_path: str | Path | None = None,
    ) -> Path:
        """Salva em disco a resposta obtida diretamente pela API da íntegra."""
        if output_path is None:
            filename = (
                f"{session.numero_processo.replace('/', '_')}_integra_http"
                f"{self._extension_for_content_type(response.headers.get('content-type', ''))}"
            )
            out = DOCUMENTS_DIR / filename
        else:
            out = Path(output_path)

        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(response.content)
        return out

    def fetch_with_token(
        self,
        session: CaptchaSession,
        extra_params: dict | None = None,
    ) -> httpx.Response:
        """
        Faz uma requisição à API do PJe usando o tokenCaptcha obtido.

        Note:
            A íntegra é exposta pelo TRT-6 em GET /processos/{processo_id}/integra?tokenCaptcha={token}.
        """
        params = {"tokenCaptcha": session.token_captcha}
        if extra_params:
            params.update(extra_params)

        url = f"{PJE_PROCESSOS_API_BASE}/{session.processo_id}/integra"
        resp = httpx.get(
            url,
            params=params,
            headers={
                "x-grau-instancia": session.grau,
                "accept": "application/json, text/plain, */*",
                "content-type": "application/json",
            },
            timeout=30,
            follow_redirects=True,
        )
        resp.raise_for_status()
        return resp

    @staticmethod
    def _extension_for_content_type(content_type: str) -> str:
        normalized = content_type.lower()
        if "application/pdf" in normalized:
            return ".pdf"
        if "application/json" in normalized:
            return ".json"
        if "text/html" in normalized:
            return ".html"
        return ".bin"
