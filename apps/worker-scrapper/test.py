import json
import os
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from pje_scraper.captcha import CaptchaSolver

solver = CaptchaSolver()

BASE_DIR = Path(__file__).resolve().parent
IMAGES_JSON = BASE_DIR / "data" / "images.json"
TEST_OUTPUT_DIR = BASE_DIR / "tests" / "artifacts"


def bytes_to_img(data: bytes) -> np.ndarray:
    return cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_GRAYSCALE)


def run_case(image_file: str, expected: str | None = None) -> bool:
    TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    image_path = Path(image_file)
    if not image_path.is_absolute():
        image_path = BASE_DIR / image_path

    if not image_path.exists():
        print(f"  SKIP  {image_file} — file not found")
        return True

    with open(image_path, "rb") as f:
        raw = f.read()

    diagnostics = solver.solve_with_diagnostics(raw)
    selected_variant = diagnostics["selected_variant"]
    selected_raw = diagnostics["selected_raw"]
    selected_normalized = diagnostics["selected_normalized"]
    solved_text = diagnostics["final_text"]
    rules = diagnostics["applied_rules"]

    variants = solver._preprocess(raw)
    processed_bytes = variants.get(selected_variant, raw)

    base = image_path.stem
    before_path = TEST_OUTPUT_DIR / f"{base}_before.png"
    after_path = TEST_OUTPUT_DIR / f"{base}_after.png"
    cv2.imwrite(str(before_path), cv2.imread(str(image_path)))
    cv2.imwrite(str(after_path), bytes_to_img(processed_bytes))

    if expected:
        passed = solved_text == expected
        status = "PASS ✓" if passed else "FAIL ✗"
        print(
            f"  {status}  {image_file}"
            f"  variant={selected_variant}"
            f"  raw={repr(selected_raw)}"
            f"  normalized={repr(selected_normalized)}"
            f"  solved={repr(solved_text)}"
            f"  rules={rules}"
            f"  expected={repr(expected)}"
        )
        return passed
    else:
        print(
            f"  INFO  {image_file}"
            f"  variant={selected_variant}"
            f"  raw={repr(selected_raw)}"
            f"  normalized={repr(selected_normalized)}"
            f"  solved={repr(solved_text)}"
            f"  rules={rules}"
        )
        return True


def main():
    if len(sys.argv) > 1:
        run_case(sys.argv[1])
        return

    if not IMAGES_JSON.exists():
        print(f"No {IMAGES_JSON} found.")
        return

    with open(IMAGES_JSON) as f:
        data = json.load(f)

    cases = data.get("images", [])
    total = passed = 0

    for case in cases:
        src = case.get("src", "")
        expected = case.get("text")
        ok = run_case(src, expected)
        if expected:
            total += 1
            passed += int(ok)

    print(f"\n{passed}/{total} passed")
    if passed < total:
        sys.exit(1)


if __name__ == "__main__":
    main()
