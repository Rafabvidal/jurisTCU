from types import SimpleNamespace
from unittest.mock import MagicMock

from pje_scraper import worker as scraper_worker


def test_run_pipeline_uploads_and_triggers_llm(monkeypatch):
    fake_pipeline = MagicMock()
    fake_pipeline.resolve.return_value = SimpleNamespace(numero_processo="0001", grau="1")
    fake_pipeline.fetch_with_token.return_value = SimpleNamespace(content=b"fake-pdf")

    fake_client = MagicMock()
    fake_async_result = SimpleNamespace(id="task-123")
    fake_send_task = MagicMock(return_value=fake_async_result)

    monkeypatch.setattr(scraper_worker, "PjePipeline", MagicMock(return_value=fake_pipeline))
    monkeypatch.setattr(scraper_worker, "client", fake_client)
    monkeypatch.setattr(scraper_worker.app, "send_task", fake_send_task)

    scraper_worker.run_pipeline(numero="0001", grau="1", headless=True)

    fake_client.create_bucket.assert_called_once_with("pje-documents")
    fake_client.upload_object.assert_called_once()
    fake_send_task.assert_called_once_with(
        "worker_llm.run_pipeline",
        kwargs={
            "numero_processo": "0001",
            "grau": "1",
            "bucket_name": "pje-documents",
            "object_name": "0001_1.pdf",
        },
    )
