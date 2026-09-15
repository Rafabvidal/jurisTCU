import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from shared.constants import PDF_BUCKET, WORKER_LLM_TASK_NAME

APP_SRC = Path(__file__).resolve().parent / "src"
if str(APP_SRC) not in sys.path:
    sys.path.insert(0, str(APP_SRC))

import ingestion

ingestion.__path__.append(str(APP_SRC / "ingestion"))

import ingestion.main as main_module


@patch.object(main_module, "IngestionParser")
@patch.object(main_module, "ProcessSubmitter")
@patch.object(main_module.app, "send_task")
def test_pending_analise_dispatches_worker_llm_directly(mock_send_task, mock_submitter_cls, mock_parser_cls):
    mock_parser = Mock()
    mock_parser.pending_analise = True
    mock_parser.pending_analise_api_url = "http://api:8000/api/processos/nao_possuem_analise/"
    mock_parser_cls.return_value = mock_parser

    mock_submitter = Mock()
    mock_submitter.fetch_pending_analise.return_value = [
        SimpleNamespace(numero_processo="0001", grau="1"),
    ]
    mock_submitter_cls.return_value = mock_submitter

    main_module.main()

    mock_send_task.assert_called_once_with(
        WORKER_LLM_TASK_NAME,
        kwargs={
            "numero_processo": "0001",
            "grau": "1",
            "bucket_name": PDF_BUCKET,
            "object_name": "0001_1.pdf",
        },
    )
