from rest_framework import status

from core.models.analise import Analise
from core.tests.base import BaseProcessoViewsetTests
from core.tests.constants import (
    DATA_BASE,
    NAO_POSSUEM_ANALISE_ENDPOINT,
    PROCESSO_NUMERO_1,
    PROCESSO_NUMERO_2,
)
from core.tests.helpers import DataSetup


class TestProcessoViewsetNaoPossuemAnalise(BaseProcessoViewsetTests):
    def test_given_empty_database_when_get_nao_possuem_analise_then_return_empty_list(self) -> None:
        response = self.client.get(NAO_POSSUEM_ANALISE_ENDPOINT)

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])

    def test_given_process_without_analise_when_get_then_return_resumo_with_normalized_grau(self) -> None:
        DataSetup.create_processo_existente(
            numero_processo=PROCESSO_NUMERO_1,
            data_hora_ultima_atualizacao=DATA_BASE,
            grau="G1",
            pdf_url="s3://pje-documents/000.pdf",
        )

        response = self.client.get(NAO_POSSUEM_ANALISE_ENDPOINT)

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.json(), [{"numero_processo": PROCESSO_NUMERO_1, "grau": "1"}])

    def test_given_process_with_analise_when_get_then_do_not_return_process(self) -> None:
        analise = Analise.objects.create(resumo="Resumo teste")
        processo = DataSetup.create_processo_existente(
            numero_processo=PROCESSO_NUMERO_2,
            data_hora_ultima_atualizacao=DATA_BASE,
            grau="G2",
            pdf_url="s3://pje-documents/000.pdf",
        )
        processo.analise = analise
        processo.save(update_fields=["analise"])

        response = self.client.get(NAO_POSSUEM_ANALISE_ENDPOINT)

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])
