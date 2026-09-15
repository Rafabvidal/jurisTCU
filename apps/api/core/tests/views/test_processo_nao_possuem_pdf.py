from types import SimpleNamespace
from unittest.mock import patch

from rest_framework import status

from core.tests.base import BaseProcessoViewsetTests
from core.tests.constants import (
    DATA_BASE,
    NAO_POSSUEM_PDF_ENDPOINT,
    PROCESSO_NUMERO_1,
    PROCESSO_NUMERO_2,
)
from core.tests.helpers import DataSetup


class TestProcessoViewsetNaoPossuemPdf(BaseProcessoViewsetTests):
    def test_given_empty_database_when_get_nao_possuem_pdf_then_return_empty_list(self) -> None:
        response = self.client.get(NAO_POSSUEM_PDF_ENDPOINT)

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])

    def test_given_pdf_missing_and_absent_in_s3_when_get_then_return_resumo_with_normalized_grau(self) -> None:
        DataSetup.create_processo_existente(
            numero_processo=PROCESSO_NUMERO_1,
            data_hora_ultima_atualizacao=DATA_BASE,
            grau="G1",
            pdf_url=None,
        )

        with patch("core.services.get_s3_client") as mocked_client_factory:
            mocked_client = mocked_client_factory.return_value
            mocked_client.list_objects.return_value = []

            response = self.client.get(NAO_POSSUEM_PDF_ENDPOINT)

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.json(), [{"numero_processo": PROCESSO_NUMERO_1, "grau": "1"}])

    def test_given_pdf_missing_but_exists_in_s3_when_get_then_do_not_return_process(self) -> None:
        DataSetup.create_processo_existente(
            numero_processo=PROCESSO_NUMERO_1,
            data_hora_ultima_atualizacao=DATA_BASE,
            grau="G2",
            pdf_url="",
        )

        s3_item = SimpleNamespace(object_name=f"{PROCESSO_NUMERO_1}_2.pdf")

        with patch("core.services.get_s3_client") as mocked_client_factory:
            mocked_client = mocked_client_factory.return_value
            mocked_client.list_objects.return_value = [s3_item]

            response = self.client.get(NAO_POSSUEM_PDF_ENDPOINT)

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])

    def test_given_pdf_url_already_set_when_get_then_ignore_even_if_missing_in_s3(self) -> None:
        DataSetup.create_processo_existente(
            numero_processo=PROCESSO_NUMERO_1,
            data_hora_ultima_atualizacao=DATA_BASE,
            grau="G1",
            pdf_url="s3://pje-documents/000.pdf",
        )

        with patch("core.services.get_s3_client") as mocked_client_factory:
            mocked_client = mocked_client_factory.return_value
            mocked_client.list_objects.return_value = []

            response = self.client.get(NAO_POSSUEM_PDF_ENDPOINT)

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])

    def test_given_s3_lookup_fails_when_get_then_return_503(self) -> None:
        DataSetup.create_processo_existente(
            numero_processo=PROCESSO_NUMERO_2,
            data_hora_ultima_atualizacao=DATA_BASE,
            grau="G1",
            pdf_url=None,
        )

        with patch("core.services.get_s3_client") as mocked_client_factory:
            mocked_client = mocked_client_factory.return_value
            mocked_client.list_objects.side_effect = RuntimeError("S3 unavailable")

            response = self.client.get(NAO_POSSUEM_PDF_ENDPOINT)

        self.assert_response_fail(response, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("mensagem", response.json())
