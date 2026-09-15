"""Playwright-based scraper for pje.trt6.jus.br/consultaprocessual."""

import base64
import re
import time
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlparse

from playwright.sync_api import Page, Request, Response, sync_playwright

from .captcha import CaptchaSolver
from .models import CaptchaPdfCapture, CaptchaSession, GrauInfo, ProcessInfo

PJE_BASE = "https://pje.trt6.jus.br/consultaprocessual"
PJE_CONSULTA_API_BASE = "https://pje.trt6.jus.br/pje-consulta-api/api"
SEARCH_URL = f"{PJE_BASE}/detalhe-processo/"

def search_url(num):
    return SEARCH_URL + num


def captcha_url(num: str, grau: str) -> str:
    return f"{PJE_BASE}/captcha/detalhe-processo/{num}/{grau}"

class PjeScraper:
    """
    Scraper para o sistema PJe TRT-6.

    Usage:
        from pje_scraper import PjePipeline
        pipeline = PjePipeline()
        session = pipeline.resolve("0000573-11.2025.5.06.0021", grau="1")
        print(session.token_captcha)
    """

    def __init__(
        self,
        captcha_solver: CaptchaSolver,
        headless: bool = True,
        timeout_ms: int = 30_000,
        captcha_log_dir: Path | None = None,
        max_captcha_retries: int = 10,
    ):
        self.solver = captcha_solver
        self.headless = headless
        self.timeout_ms = timeout_ms
        self.max_captcha_retries = max_captcha_retries
        self.captcha_log_dir = (
            captcha_log_dir
            if captcha_log_dir is not None
            else Path(__file__).resolve().parent.parent / "captcha_log"
        )

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #



    def get_token_captcha(
        self,
        numero_processo: str,
        grau: str = "1",
    ) -> CaptchaSession:
        """
        Executa o fluxo completo e retorna um CaptchaSession com tokenCaptcha.

        Args:
            numero_processo: ex. "0000573-11.2025.5.06.0021"
            grau: "1" (primeiro grau) ou "2" (segundo grau)

        Returns:
            CaptchaSession com token_desafio, token_captcha e demais dados.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context()
            page = context.new_page()
            page.set_default_timeout(self.timeout_ms)

            try:
                session, _ = self._run(page, numero_processo, grau)
            finally:
                browser.close()

        return session

    def get_pdf_from_browser_flow(
        self,
        numero_processo: str,
        grau: str = "1",
        pdf_wait_ms: int = 20_000,
    ) -> CaptchaPdfCapture:
        """
        Executa o fluxo completo e intercepta o retorno da íntegra via fetch no navegador.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context()
            page = context.new_page()
            page.set_default_timeout(self.timeout_ms)

            try:
                session, state = self._run(
                    page,
                    numero_processo,
                    grau,
                    capture_pdf=True,
                    pdf_wait_ms=pdf_wait_ms,
                )
            finally:
                browser.close()

        if state["pdf_bytes"] is None:
            raise RuntimeError(
                "Process integra not captured from browser flow. "
                "No response from the integra endpoint was intercepted."
            )

        return CaptchaPdfCapture(
            session=session,
            pdf_bytes=state["pdf_bytes"],
            pdf_url=state["pdf_url"] or "",
            content_type=state["pdf_content_type"] or "application/pdf",
        )

    def search_process(self, numero_processo: str) -> ProcessInfo:
        """
        Somente busca o processo e retorna os graus disponíveis (sem resolver captcha).
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context()
            page = context.new_page()
            page.set_default_timeout(self.timeout_ms)

            try:
                info = self._search(page, numero_processo)
            finally:
                browser.close()

        return info

    # ------------------------------------------------------------------ #
    #  Internal steps                                                      #
    # ------------------------------------------------------------------ #

    def _run(
        self,
        page: Page,
        numero_processo: str,
        grau: str,
        capture_pdf: bool = False,
        pdf_wait_ms: int = 20_000,
    ) -> tuple[CaptchaSession, dict]:
        # Containers for intercepted values
        state: dict = {
            "token_desafio": None,
            "token_captcha": None,
            "processo_id": None,
            "grau": grau,
            "pdf_bytes": None,
            "pdf_url": None,
            "pdf_content_type": None,
        }

        # ---- Intercept requests to extract tokens ---- #
        def on_request(req: Request):
            url = req.url
            parsed = urlparse(url)
            qs = parse_qs(parsed.query)

            process_match = re.search(r"/api/processos/(\d+)(?:/|$)", parsed.path)
            if process_match:
                state["processo_id"] = process_match.group(1)

            captcha_process_id = qs.get("idProcesso", [None])[0]
            if captcha_process_id:
                state["processo_id"] = captcha_process_id

            # Match requests like .../XXXXXXX?tokenDesafio=... or ?tokenCaptcha=...
            if "tokenDesafio=" in url:
                state["token_desafio"] = qs.get("tokenDesafio", [None])[0]
                # Extract processo ID from path: last numeric segment before '?'
                path_segment = parsed.path.rstrip("/").split("/")[-1]
                if path_segment.isdigit():
                    state["processo_id"] = path_segment
            elif "tokenCaptcha=" in url:
                state["token_captcha"] = qs.get("tokenCaptcha", [None])[0]
                if state["processo_id"] is None:
                    path_segment = parsed.path.rstrip("/").split("/")[-1]
                    if path_segment.isdigit():
                        state["processo_id"] = path_segment

        def on_response(resp: Response):
            if not capture_pdf:
                return

            url = resp.url
            if "/api/processos/" not in url or "/integra" not in url or "tokenCaptcha=" not in url:
                return

            try:
                state["pdf_bytes"] = resp.body()
                state["pdf_url"] = url
                state["pdf_content_type"] = (resp.headers.get("content-type") or "application/octet-stream").lower()
            except Exception:
                return

        page.on("request", on_request)
        page.on("response", on_response)

        # Step 1 – Navigate to search page
        page.goto(search_url(numero_processo), wait_until="networkidle")

        # Step 2 – Handle multi-grau selection before captcha.
        self._navigate_to_requested_grau(page, numero_processo, grau)

        # Step 4 – Wait for captcha page
        page.wait_for_selector("#imagemCaptcha", timeout=self.timeout_ms)

        # Steps 5-7 – Solve and submit (with automatic retry on wrong answer)
        captcha_text = self._captcha_solve_loop(page, state, numero_processo, grau)

        if capture_pdf:
            self._request_process_integra(page, state)
            self._wait_for_pdf_capture(page, state, max_wait_ms=pdf_wait_ms)

        if state["token_captcha"] is None:
            raise RuntimeError(
                "tokenCaptcha not captured. Possible wrong captcha answer or page error."
            )
        if state["token_desafio"] is None:
            raise RuntimeError("tokenDesafio not captured from network requests.")
        if state["processo_id"] is None:
            raise RuntimeError("processo_id not captured from TRT-6 API requests.")

        session = CaptchaSession(
            numero_processo=numero_processo,
            grau=grau,
            processo_id=state["processo_id"] or "",
            token_desafio=state["token_desafio"],
            token_captcha=state["token_captcha"],
            captcha_text=captcha_text,
        )
        return session, state

    def _search(self, page: Page, numero_processo: str) -> ProcessInfo:
        page.goto(SEARCH_URL, wait_until="networkidle")
        page.fill("#nrProcessoInput", numero_processo)
        page.click("#btnPesquisar")
        page.wait_for_load_state("networkidle")
        return self._detect_graus(page)

    def _navigate_to_requested_grau(
        self,
        page: Page,
        numero_processo: str,
        grau: str,
    ) -> None:
        if page.locator("#imagemCaptcha").count() > 0:
            return

        grau_pattern = re.compile(rf"{re.escape(grau)}\s*[°ºo]?\s*grau", re.IGNORECASE)

        # Multi-grau screen in TRT-6 commonly renders process options as buttons.
        grau_button = page.locator("button.selecao-processo").filter(has_text=grau_pattern)
        if grau_button.count() > 0:
            grau_button.first.click()
            page.wait_for_load_state("networkidle")

        if page.locator("#imagemCaptcha").count() > 0:
            return

        grau_link = page.get_by_role("link", name=grau_pattern)
        if grau_link.count() > 0:
            grau_link.first.click()
            page.wait_for_load_state("networkidle")

        if page.locator("#imagemCaptcha").count() > 0:
            return

        process_info = self._detect_graus(page)
        if process_info.graus:
            target_grau = self._find_grau(process_info.graus, grau)
            target_url = target_grau.url or captcha_url(numero_processo, target_grau.grau)
            page.goto(urljoin(page.url, target_url), wait_until="networkidle")
            return

        direct_url = captcha_url(numero_processo, grau)
        if page.url.rstrip("/") != direct_url.rstrip("/"):
            page.goto(direct_url, wait_until="networkidle")

    def _detect_graus(self, page: Page) -> ProcessInfo:
        """
        Detecta se a página mostra múltiplos graus (links 1°/2° Grau) ou
        redireciona diretamente para o processo.
        """
        # Check for grau links: "PJe 1° Grau" / "PJe 2° Grau"
        # The "mais de um grau" page shows links like href="https://pje.trt6.jus.br/primeirograu"
        # but the consultaprocessual app shows grau selection inside its own router.
        # We look for links containing "primeirograu" or "segundograu" in their href,
        # or for elements that contain the text "1° Grau" / "2° Grau".
        # Extract processo number from URL to build deterministic fallback URLs.
        current_url = page.url
        numero_match = re.search(r"(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})", current_url)
        numero = numero_match.group(1) if numero_match else ""

        graus = []
        grau_links = page.query_selector_all("a[href*='primeirograu'], a[href*='segundograu']")
        for link in grau_links:
            href = link.get_attribute("href") or ""
            text = (link.inner_text() or "").strip()
            if "primeirograu" in href:
                graus.append(GrauInfo(grau="1", label=text or "PJe 1° Grau", url=href))
            elif "segundograu" in href:
                graus.append(GrauInfo(grau="2", label=text or "PJe 2° Grau", url=href))

        # Fallback: Angular router-based grau selection (internal links)
        if not graus:
            grau_links_ng = page.query_selector_all("a[href*='detalhe-processo']")
            for link in grau_links_ng:
                href = link.get_attribute("href") or ""
                text = (link.inner_text() or "").strip()
                # Try to infer grau from text
                g = "1" if "1" in text else ("2" if "2" in text else "?")
                graus.append(GrauInfo(grau=g, label=text, url=href))

        # Current TRT-6 page uses buttons for grau selection on multi-process screen.
        if not graus:
            grau_buttons = page.query_selector_all("button.selecao-processo")
            for btn in grau_buttons:
                text = (btn.inner_text() or "").strip()
                g = "1" if re.search(r"\b1\s*[°ºo]?\s*grau\b", text, re.IGNORECASE) else (
                    "2" if re.search(r"\b2\s*[°ºo]?\s*grau\b", text, re.IGNORECASE) else "?"
                )
                url = captcha_url(numero or "", g) if g in {"1", "2"} and numero else ""
                graus.append(GrauInfo(grau=g, label=text, url=url))

        return ProcessInfo(
            numero=numero,
            graus=graus,
            single_url=current_url if not graus else None,
        )

    def _find_grau(self, graus: list[GrauInfo], grau: str) -> GrauInfo:
        for g in graus:
            if g.grau == grau:
                return g
        # Fallback: first available
        return graus[0]

    def _captcha_solve_loop(
        self,
        page: Page,
        state: dict,
        numero_processo: str,
        grau: str,
    ) -> str:
        """
        Extrai, resolve e submete o captcha com retry automático em caso de resposta errada.

        Em cada tentativa:
          - Salva a imagem do captcha em captcha_log_dir com sufixo `success` ou `failure`.
          - Em caso de falha (snackbar "inválidos"), recarrega a página para obter novo desafio.

        Returns:
            O texto do captcha que resultou em tokenCaptcha válido.
        """
        self.captcha_log_dir.mkdir(parents=True, exist_ok=True)

        for attempt in range(1, self.max_captcha_retries + 1):
            captcha_src: str = page.get_attribute("#imagemCaptcha", "src") or ""
            img_bytes = self._decode_captcha_bytes(captcha_src)

            # Solve via OCR once per challenge. If short, refresh challenge and retry.
            captcha_text = self.solver.solve_base64(captcha_src)
            if len(captcha_text) < 6:
                self._save_captcha(img_bytes, captcha_text, attempt, "invalid_short")
                print(
                    f"[!] Captcha curto ({captcha_text!r}) "
                    f"(attempt {attempt}/{self.max_captcha_retries}), recarregando desafio..."
                )
                state["token_desafio"] = None
                state["token_captcha"] = None
                self._reload_captcha_challenge(page, numero_processo, grau)
                continue

            print(
                f"[*] Captcha attempt {attempt}/{self.max_captcha_retries}:"
                f" text={captcha_text!r}"
            )

            # Take before-screenshot into captcha_log_dir
            page.screenshot(
                path=str(self.captcha_log_dir / f"attempt{attempt}_before.png"),
                full_page=True,
            )
            page.fill("#captchaInput", captcha_text)
            page.click("#btnEnviar")
            page.screenshot(
                path=str(self.captcha_log_dir / f"attempt{attempt}_after.png"),
                full_page=True,
            )

            outcome = self._wait_for_captcha_result(page, state)
            self._save_captcha(img_bytes, captcha_text, attempt, outcome)

            if outcome == "success":
                return captcha_text

            # Treat timeout as retryable failure as well. In production, some failures
            # do not render snackbar quickly/consistently in headless mode.
            if outcome in {"failure", "timeout"}:
                print(
                    f"[!] Captcha não validado ({outcome}) "
                    f"(attempt {attempt}/{self.max_captcha_retries}), recarregando desafio..."
                )

            state["token_desafio"] = None
            state["token_captcha"] = None
            self._reload_captcha_challenge(page, numero_processo, grau)

        raise RuntimeError(
            f"Captcha not solved after {self.max_captcha_retries} attempts "
            "(no tokenCaptcha captured)."
        )

    def _reload_captcha_challenge(self, page: Page, numero_processo: str, grau: str) -> None:
        """Recarrega rapidamente o desafio do captcha e garante a tela correta."""
        try:
            current_url = page.url or ""
            if "/captcha/detalhe-processo/" in current_url:
                page.reload(wait_until="networkidle")
            else:
                page.goto(search_url(numero_processo), wait_until="networkidle")
                self._navigate_to_requested_grau(page, numero_processo, grau)
        except Exception:
            page.goto(captcha_url(numero_processo, grau), wait_until="networkidle")

        page.wait_for_selector("#imagemCaptcha", timeout=self.timeout_ms)

    def _wait_for_captcha_result(
        self,
        page: Page,
        state: dict,
        max_wait_ms: int = 15_000,
    ) -> str:
        """
        Aguarda o resultado do submit do captcha.

        Returns:
            'success'  – tokenCaptcha capturado na rede (resposta correta)
            'failure'  – snackbar "inválidos" detectado (resposta errada)
            'timeout'  – sem resultado no tempo limite
        """
        deadline = time.time() + max_wait_ms / 1000
        while time.time() < deadline:
            if state["token_captcha"] is not None:
                return "success"

            # Snackbar with invalid message = wrong answer.
            try:
                message_selectors = (
                    "simple-snack-bar span, "
                    ".mat-simple-snackbar span, "
                    "snack-bar-container span"
                )
                for el in page.query_selector_all(message_selectors):
                    text = (el.inner_text() or "").strip().lower()
                    if not text:
                        continue
                    if (
                        "invál" in text
                        or "invalid" in text
                        or "tente novamente" in text
                        or "caracteres informados" in text
                    ):
                        return "failure"
            except Exception:
                pass

            page.wait_for_timeout(300)

        return "timeout"

    @staticmethod
    def _decode_captcha_bytes(captcha_src: str) -> bytes:
        """Decodifica a imagem captcha (base64 data URI) para bytes brutos."""
        if "base64," in captcha_src:
            return base64.b64decode(captcha_src.split("base64,", 1)[1].strip())
        return base64.b64decode(captcha_src)

    def _save_captcha(
        self,
        img_bytes: bytes,
        captcha_text: str,
        attempt: int,
        outcome: str,
    ) -> None:
        """Salva a imagem do captcha em captcha_log_dir para análise posterior."""
        ts = int(time.time() * 1000)
        safe_text = "".join(c for c in captcha_text if c.isalnum())
        filename = f"{ts}_a{attempt}_{safe_text}_{outcome}.png"
        path = self.captcha_log_dir / filename
        path.write_bytes(img_bytes)
        print(f"[*] Captcha salvo: {path.name}")

    def _request_process_integra(self, page: Page, state: dict) -> None:
        """Dispara explicitamente o fetch da íntegra usando o tokenCaptcha capturado."""
        processo_id = state.get("processo_id")
        token_captcha = state.get("token_captcha")
        grau = state.get("grau")
        if not processo_id or not token_captcha:
            raise RuntimeError("Cannot request process integra without processo_id and tokenCaptcha.")

        result = page.evaluate(
            """
            async ({ processoId, tokenCaptcha, grau, apiBase }) => {
                const url = `${apiBase}/processos/${processoId}/integra?tokenCaptcha=${encodeURIComponent(tokenCaptcha)}`;
                const response = await fetch(url, {
                    credentials: 'include',
                    headers: {
                        'x-grau-instancia': String(grau),
                        'accept': 'application/json, text/plain, */*',
                        'content-type': 'application/json'
                    }
                });
                await response.arrayBuffer();
                return {
                    ok: response.ok,
                    status: response.status,
                    url: response.url,
                    contentType: response.headers.get('content-type') || ''
                };
            }
            """,
            {
                "processoId": processo_id,
                "tokenCaptcha": token_captcha,
                "grau": grau,
                "apiBase": PJE_CONSULTA_API_BASE,
            },
        )

        if not result["ok"]:
            raise RuntimeError(
                "Integra request failed "
                f"(status={result['status']}, content_type={result['contentType']!r})."
            )

    def _wait_for_pdf_capture(self, page: Page, state: dict, max_wait_ms: int = 20_000) -> None:
        """Aguarda a interceptação da resposta da íntegra após o envio do captcha."""
        deadline = time.time() + max_wait_ms / 1000
        while time.time() < deadline:
            if state["pdf_bytes"] is not None:
                return
            page.wait_for_timeout(300)

        raise RuntimeError("Timed out waiting for process integra capture.")


