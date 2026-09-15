import os
import tempfile
from pathlib import Path

import requests
from main import analyze_file
from shared.celery_client import app
from shared.logger import get_logger
from shared.s3_client import get_s3_client

logger = get_logger("worker_llm")
DEFAULT_API_URL = "http://api:8000/api/processos/adicionar_analise/"


def _build_payload(numero_processo: str, grau: str, analise) -> dict:
    analise_data = analise.model_dump(mode="json") if hasattr(analise, "model_dump") else dict(analise)
    analise_data.pop("numero_processo", None)

    return {
        "numero_processo": numero_processo,
        "grau": grau,
        "analise": analise_data,
    }


def process_llm_pipeline(
    numero_processo: str,
    grau: str,
    bucket_name: str,
    object_name: str,
    api_url: str,
) -> dict:
    client = get_s3_client()
    suffix = Path(object_name).suffix or ".pdf"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = tmp.name

    try:
        logger.info(
            "Baixando PDF para análise: numero_processo=%s grau=%s bucket=%s object_name=%s tmp_path=%s",
            numero_processo,
            grau,
            bucket_name,
            object_name,
            tmp_path,
        )
        client.get_object(bucket_name, object_name, tmp_path)

        analise = analyze_file(tmp_path)

        payload = _build_payload(numero_processo, grau, analise)

        response = requests.post(api_url, json=payload, timeout=30)

        response.raise_for_status()

        logger.info(
            "Analise enviada para API: numero_processo=%s grau=%s bucket=%s object_name=%s",
            numero_processo,
            grau,
            bucket_name,
            object_name,
        )
        return payload
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.task(bind=True, name="worker_llm.run_pipeline", max_retries=3, default_retry_delay=30)
def run_pipeline(self, numero_processo: str, grau: str, bucket_name: str, object_name: str):
    api_url = os.getenv("WORKER_LLM_API_URL", DEFAULT_API_URL)

    logger.info(
        "Iniciando task LLM: task_id=%s numero_processo=%s grau=%s bucket=%s object_name=%s",
        self.request.id,
        numero_processo,
        grau,
        bucket_name,
        object_name,
    )

    try:
        return process_llm_pipeline(
            numero_processo=numero_processo,
            grau=grau,
            bucket_name=bucket_name,
            object_name=object_name,
            api_url=api_url,
        )
    except Exception as exc:
        logger.exception(
            "Falha na task LLM. Reagendando tentativa: task_id=%s numero_processo=%s grau=%s",
            self.request.id,
            numero_processo,
            grau,
        )
        raise self.retry(exc=exc) from exc
