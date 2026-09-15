from rest_framework import status

from core.models.processo import Processo
from core.tests.base import BaseProcessoViewsetTests
from core.tests.constants import DATA_BASE, PROCESSO_NUMERO_1, TRIBUNAL_TRT6
from core.tests.helpers import DataSetup

ADICIONAR_ANALISE_ENDPOINT = "/api/processos/adicionar_analise/"


class TestProcessoViewsetAdicionarAnalise(BaseProcessoViewsetTests):
    def test_given_existing_processo_when_post_adicionar_analise_then_create_analysis(self) -> None:
        DataSetup.create_processo_existente(
            numero_processo=PROCESSO_NUMERO_1,
            data_hora_ultima_atualizacao=DATA_BASE,
            tribunal=TRIBUNAL_TRT6,
            grau="G1",
        )

        payload = {
            "numero_processo": PROCESSO_NUMERO_1,
            "grau": "1",
            "analise": {
                "resumo": "Resumo teste",
                "tipo_ato_principal": "sentenca",
                "decisao": "Decisao teste",
                "palavras_chave": ["trabalho", "rescisao"],
                "status": "sentenciado",
                "desfecho": "sentenca_procedente",
                "resultado_reclamante": "ganhou",
                "valor_causa": "1234.56",
                "custas_valor_total": "99.99",
            },
        }

        response = self.client.post(ADICIONAR_ANALISE_ENDPOINT, payload, format="json")

        self.assert_response_success(response, status.HTTP_200_OK)
        processo = Processo.objects.get(numero_processo=PROCESSO_NUMERO_1, grau="G1")
        self.assertIsNotNone(processo.analise)
        self.assertEqual(processo.analise.resumo, "Resumo teste")
        self.assertEqual(processo.analise.palavras_chave.count(), 2)

    def test_given_existing_analysis_when_post_adicionar_analise_then_update_existing(self) -> None:
        processo = DataSetup.create_processo_existente(
            numero_processo=PROCESSO_NUMERO_1,
            data_hora_ultima_atualizacao=DATA_BASE,
            tribunal=TRIBUNAL_TRT6,
            grau="G1",
        )

        first_payload = {
            "numero_processo": PROCESSO_NUMERO_1,
            "grau": "1",
            "analise": {
                "resumo": "Resumo inicial",
                "palavras_chave": ["inicial"],
                "status": "em_andamento",
            },
        }
        second_payload = {
            "numero_processo": PROCESSO_NUMERO_1,
            "grau": "1",
            "analise": {
                "resumo": "Resumo updated",
                "palavras_chave": ["atualizado", "final"],
                "status": "arquivado",
            },
        }

        response_1 = self.client.post(ADICIONAR_ANALISE_ENDPOINT, first_payload, format="json")
        self.assert_response_success(response_1, status.HTTP_200_OK)
        analise_id = Processo.objects.get(pk=processo.pk).analise_id

        response_2 = self.client.post(ADICIONAR_ANALISE_ENDPOINT, second_payload, format="json")
        self.assert_response_success(response_2, status.HTTP_200_OK)

        processo.refresh_from_db()
        self.assertEqual(processo.analise_id, analise_id)
        self.assertEqual(processo.analise.resumo, "Resumo updated")
        self.assertEqual(processo.analise.status, "arquivado")
        self.assertEqual(sorted([p.nome for p in processo.analise.palavras_chave.all()]), ["atualizado", "final"])

    def test_given_missing_processo_when_post_adicionar_analise_then_return_404(self) -> None:
        payload = {
            "numero_processo": PROCESSO_NUMERO_1,
            "grau": "1",
            "analise": {
                "resumo": "Resumo teste",
                "palavras_chave": ["chave"],
            },
        }

        response = self.client.post(ADICIONAR_ANALISE_ENDPOINT, payload, format="json")

        self.assert_response_not_found(response)
        self.assertIn("mensagem", response.json())

    def test_given_desfecho_value_in_status_when_post_adicionar_analise_then_normalize_and_accept(self) -> None:
        DataSetup.create_processo_existente(
            numero_processo=PROCESSO_NUMERO_1,
            data_hora_ultima_atualizacao=DATA_BASE,
            tribunal=TRIBUNAL_TRT6,
            grau="G1",
        )

        payload = {
            "numero_processo": PROCESSO_NUMERO_1,
            "grau": "1",
            "analise": {
                "resumo": "Resumo teste",
                "status": "arquivado_sem_decisao",
                "desfecho": "arquivado_sem_decisao",
                "palavras_chave": ["teste"],
            },
        }

        response = self.client.post(ADICIONAR_ANALISE_ENDPOINT, payload, format="json")

        self.assert_response_success(response, status.HTTP_200_OK)
        processo = Processo.objects.get(numero_processo=PROCESSO_NUMERO_1, grau="G1")
        self.assertIsNotNone(processo.analise)
        self.assertEqual(processo.analise.status, "arquivado")
        self.assertEqual(processo.analise.desfecho, "arquivado_sem_decisao")
