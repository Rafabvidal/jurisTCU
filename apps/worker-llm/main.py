
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import opendataloader_pdf
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from shared.env_manager import EnviromentManager
from shared.llm_constants import SYSTEM_PROMPT
from shared.logger import get_logger
from shared.schemas.resumo_ia import ProcessoAnalise

DEFAULT_INPUT_PATH = "output/mock.md"

env_manager = EnviromentManager()
logger = get_logger("worker_llm")

def build_system_prompt() -> str:
    return SYSTEM_PROMPT

def _build_llm() -> ChatOpenAI:
    return ChatOpenAI(
        base_url=env_manager.get_lmstudio_base_url(),
        api_key=env_manager.get_lmstudio_api_key(),
        model_name=env_manager.get_lmstudio_model(),
    )


def _markdown_from_pdf(pdf_path: Path) -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        logger.info("Convertendo PDF para markdown: pdf_path=%s", pdf_path)
        opendataloader_pdf.convert(
            input_path=[str(pdf_path)],
            output_dir=tmpdir,
            image_output="off",
            format="markdown",
        )
        generated = sorted(Path(tmpdir).glob("*.md"))
        if not generated:
            raise RuntimeError("Nao foi possivel extrair markdown do PDF.")
        return generated[0].read_text(encoding="utf-8")


def extract_text_from_document(path: str) -> str:
    input_path = Path(path)
    logger.info("Lendo documento para análise: path=%s suffix=%s", input_path, input_path.suffix.lower())
    if input_path.suffix.lower() == ".pdf":
        return _markdown_from_pdf(input_path)
    return input_path.read_text(encoding="utf-8")


def analyze_text(pdf_text: str) -> ProcessoAnalise:

    model_name = env_manager.get_lmstudio_model()

    agent = create_agent(
        model=_build_llm(),
        response_format=ProcessoAnalise.SCHEMA,
    )

    try:
        response = agent.invoke(
            {
                "messages": [
                    {"role": "system", "content": build_system_prompt()},
                    {"role": "user", "content": f"Texto extraído do PDF:\n{pdf_text}"},
                ]
            }
        )
    except Exception:
        logger.exception("Falha ao invocar LLM com structured output: model=%s", model_name)
        raise

    if "structured_response" not in response:
        logger.error("LLM não retornou structured_response: keys=%s", sorted(response.keys()))
        raise RuntimeError("LLM nao retornou structured_response.")

    try:
        validated_analise = ProcessoAnalise.model_validate(response["structured_response"])
        logger.info("LLM retornou structured_response com sucesso e validado pelo Pydantic: model=%s", model_name)
        return validated_analise
    except Exception as e:
        logger.error("Falha na validação Pydantic dos dados retornados pela LLM: %s. Dados recebidos: %s", str(e), response["structured_response"])
        raise RuntimeError(f"Retorno da LLM violou o esquema do ProcessoAnalise: {e}") from e


def analyze_file(file_path: str) -> ProcessoAnalise:
    return analyze_text(extract_text_from_document(file_path))


def save_response(result: Any, path: str = "result.json"):
    with open(path, "w", encoding="utf-8") as f:
        if hasattr(result, "model_dump"):
            json.dump(result.model_dump(mode="json"), f, ensure_ascii=False, indent=2)
        elif isinstance(result, dict):
            json.dump(result, f, ensure_ascii=False, indent=2)
        else:
            f.write(str(result))


def main():
    input_path = os.getenv("WORKER_LLM_INPUT_PATH", DEFAULT_INPUT_PATH)
    logger.info("Iniciando análise local: input_path=%s", input_path)
    response = analyze_file(input_path)
    save_response(response)


if __name__ == "__main__":
    main()
