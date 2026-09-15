import base64

import ddddocr

from .captcha_services import (
    CaptchaCandidateSelector,
    CaptchaPostCorrector,
    CaptchaPreprocessor,
    CaptchaTextNormalizer,
)


class CaptchaSolver:
    """
    Resolve captchas usando a biblioteca ddddocr diretamente (sem servico HTTP).
    """

    def __init__(self):
        self._ocr = ddddocr.DdddOcr(show_ad=False)
        self._preprocessor = CaptchaPreprocessor()
        self._normalizer = CaptchaTextNormalizer()
        self._post_corrector = CaptchaPostCorrector()
        self._selector = CaptchaCandidateSelector(expected_length=6)

    def _preprocess(self, image_bytes: bytes) -> dict[str, bytes]:
        return self._preprocessor.generate_variants(image_bytes)

    def solve_with_diagnostics(self, image_bytes: bytes) -> dict:
        """Resolve captcha e retorna diagnostico detalhado do processo OCR."""
        variants = self._preprocess(image_bytes)

        candidates: list[dict] = []
        for variant_name, variant_bytes in variants.items():
            raw_text = self._ocr.classification(variant_bytes)
            normalized_text, norm_traces = self._normalizer.normalize(raw_text)
            candidates.append(
                {
                    "variant": variant_name,
                    "raw": raw_text,
                    "normalized": normalized_text,
                    "normalize_traces": norm_traces,
                    "score": self._selector.score(normalized_text, variant_name),
                }
            )

        selected = self._selector.select(candidates)

        corrected_text, correction_traces = self._post_corrector.apply(selected["normalized"])
        applied_rules = selected["normalize_traces"] + correction_traces

        return {
            "selected_variant": selected["variant"],
            "selected_raw": selected["raw"],
            "selected_normalized": selected["normalized"],
            "final_text": corrected_text,
            "applied_rules": applied_rules,
            "candidates": candidates,
        }

    def solve(self, image_bytes: bytes) -> str:
        """Resolve um captcha a partir dos bytes da imagem."""
        diagnostics = self.solve_with_diagnostics(image_bytes)
        return diagnostics["final_text"]

    def solve_base64(self, b64_image: str) -> str:
        """Resolve um captcha a partir de uma string base64 (com ou sem prefixo data:image/...)."""
        if "base64," in b64_image:
            b64_image = b64_image.split("base64,", 1)[1].strip()

        diagnostics = self.solve_with_diagnostics(base64.b64decode(b64_image))
        text = diagnostics["final_text"]
        print(
            "[*] Captcha OCR"
            f" variant={diagnostics['selected_variant']}"
            f" raw={diagnostics['selected_raw']!r}"
            f" normalized={diagnostics['selected_normalized']!r}"
            f" final={text!r}"
            f" rules={diagnostics['applied_rules']}"
        )
        return text
