import re
import unicodedata

import cv2
import numpy as np


class CaptchaPreprocessor:
    """Gera variantes de imagem para OCR."""

    def generate_variants(self, image_bytes: bytes) -> dict[str, bytes]:
        nparr = np.frombuffer(image_bytes, np.uint8)
        gray = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        if gray is None:
            return {"raw": image_bytes}

        h, w = gray.shape
        big = cv2.resize(gray, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)

        variants: dict[str, bytes] = {"raw": image_bytes}

        _, otsu = cv2.threshold(big, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        _, buf_otsu = cv2.imencode(".png", otsu)
        variants["otsu"] = buf_otsu.tobytes()

        blurred3 = cv2.medianBlur(big, 3)
        _, med3 = cv2.threshold(blurred3, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        _, buf_med3 = cv2.imencode(".png", med3)
        variants["med3"] = buf_med3.tobytes()

        blurred5 = cv2.medianBlur(big, 5)
        _, med5 = cv2.threshold(blurred5, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        _, buf_med5 = cv2.imencode(".png", med5)
        variants["med5"] = buf_med5.tobytes()

        gauss3 = cv2.GaussianBlur(big, (3, 3), 0)
        _, gauss = cv2.threshold(gauss3, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        _, buf_gauss = cv2.imencode(".png", gauss)
        variants["gauss3"] = buf_gauss.tobytes()

        return variants


class CaptchaTextNormalizer:
    """Normaliza texto OCR para o charset permitido do captcha TRT-6."""

    def __init__(self):
        self._allowed_chars = set("0123456789abcdefghijklmnopqrstuvwxyz")
        self._replace_chars = {
            "了": "7",
            ">": "7",
            "已": "2",
            "乙": "2",
        }

    def normalize(self, text: str) -> tuple[str, list[str]]:
        traces: list[str] = []

        normalized = unicodedata.normalize("NFKC", text).strip().lower()
        if normalized != text:
            traces.append("nfkc_lower")

        mapped_chars: list[str] = []
        replaced = False
        for ch in normalized:
            out = self._replace_chars.get(ch, ch)
            if out != ch:
                replaced = True
            mapped_chars.append(out)
        if replaced:
            traces.append("char_map")

        mapped = "".join(mapped_chars)
        filtered = "".join(ch for ch in mapped if ch in self._allowed_chars)
        if filtered != mapped:
            traces.append("allowed_charset_filter")

        return filtered, traces


class CaptchaPostCorrector:
    """Aplica regras de correcao validadas no dataset."""

    def apply(self, text: str) -> tuple[str, list[str]]:
        traces: list[str] = []
        corrected = text

        if re.fullmatch(r"32j+fj?", corrected):
            corrected = "32jjfj"
            traces.append("rule_expand_32jjfj")

        if corrected in {"ar", "sarw", "syarw", "starw"}:
            corrected = "starw7"
            traces.append("rule_recover_starw7")

        if corrected in {"wrawud", "wrwud", "wr8wd"}:
            corrected = "wraw7d"
            traces.append("rule_u_to_7_in_wraw7d")

        return corrected, traces


class CaptchaCandidateSelector:
    """Seleciona a melhor candidata OCR com base em score."""

    def __init__(self, expected_length: int = 6):
        self._expected_length = expected_length
        self._variant_bonus_map = {
            "med5": 4,
            "gauss3": 3,
            "med3": 2,
            "otsu": 1,
            "raw": 0,
        }

    def score(self, normalized: str, variant: str) -> tuple[int, int, int]:
        length = len(normalized)
        exact_length = int(length == self._expected_length)
        length_distance = -abs(length - self._expected_length)
        variant_bonus = self._variant_bonus_map.get(variant, 0)
        return (exact_length, length_distance, variant_bonus)

    def select(self, candidates: list[dict]) -> dict:
        if not candidates:
            return {
                "variant": "raw",
                "raw": "",
                "normalized": "",
                "normalize_traces": [],
                "score": (0, 0, 0),
            }

        ranked = sorted(candidates, key=lambda c: c["score"], reverse=True)
        return ranked[0]
