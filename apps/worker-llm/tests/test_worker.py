import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import requests
import worker

APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))



def test_process_llm_pipeline_downloads_analyzes_and_posts(monkeypatch):
    fake_client = MagicMock()
    fake_analise = MagicMock()
    fake_analise.model_dump.return_value = {
        "numero_processo": "0001",
        "resumo": "ok",
        "palavras_chave": ["a", "b"],
    }

    fake_response = MagicMock()
    fake_response.raise_for_status.return_value = None

    monkeypatch.setattr(worker, "get_s3_client", MagicMock(return_value=fake_client))
    monkeypatch.setattr(worker, "analyze_file", MagicMock(return_value=fake_analise))
    monkeypatch.setattr(worker.requests, "post", MagicMock(return_value=fake_response))

    payload = worker.process_llm_pipeline(
        numero_processo="0001",
        grau="1",
        bucket_name="pje-documents",
        object_name="0001_1.pdf",
        api_url="http://localhost:8000/api/processos/adicionar_analise/",
    )

    fake_client.get_object.assert_called_once()
    worker.requests.post.assert_called_once()
    assert payload["numero_processo"] == "0001"
    assert payload["grau"] == "1"
    assert payload["analise"]["resumo"] == "ok"
    assert "numero_processo" not in payload["analise"]


def test_run_pipeline_retries_on_failure(monkeypatch):
    monkeypatch.setattr(worker, "process_llm_pipeline", MagicMock(side_effect=RuntimeError("boom")))

    with pytest.raises(RuntimeError, match="retry-called"):
        monkeypatch.setattr(worker.run_pipeline, "retry", MagicMock(side_effect=RuntimeError("retry-called")))
        worker.run_pipeline(
            numero_processo="0001",
            grau="1",
            bucket_name="pje-documents",
            object_name="0001_1.pdf",
        )

    worker.run_pipeline.retry.assert_called_once()


def test_run_pipeline_does_not_retry_on_http_400(monkeypatch):
    fake_response = MagicMock()
    fake_response.status_code = 400
    exc = requests.exceptions.HTTPError(response=fake_response)

    monkeypatch.setattr(worker, "process_llm_pipeline", MagicMock(side_effect=exc))
    monkeypatch.setattr(worker.run_pipeline, "retry", MagicMock(side_effect=RuntimeError("retry-called")))

    with pytest.raises(requests.exceptions.HTTPError):
        worker.run_pipeline(
            numero_processo="0001",
            grau="1",
            bucket_name="pje-documents",
            object_name="0001_1.pdf",
        )

    worker.run_pipeline.retry.assert_not_called()


def test_default_llm_base_url_is_valid(monkeypatch):
    monkeypatch.delenv("WORKER_LLM_BASE_URL", raising=False)

    from main import _build_llm

    llm = _build_llm()
    assert llm.openai_api_base == "http://host.docker.internal:1234/v1"
