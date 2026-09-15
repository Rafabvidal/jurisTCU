from unittest.mock import patch

from django.db import IntegrityError
from rest_framework import status

from core.models.assunto import Assunto
from core.models.classe import Classe
from core.models.orgao_julgador import OrgaoJulgador
from core.models.processo import Processo
from core.tests.base import BaseProcessoViewsetTests
from core.tests.constants import (
    DATA_BASE,
    DATA_NOVA,
    DEDUPLICAR_ENDPOINT,
    PROCESSO_NUMERO_1,
    PROCESSO_NUMERO_2,
    RESUMO_RESPONSE_KEYS,
)
from core.tests.helpers import DataSetup, ProcessoPayloadBuilder


class TestProcessoViewsetDeduplicar(BaseProcessoViewsetTests):
    def test_given_empty_payload_when_post_deduplicar_then_return_empty_list(self) -> None:
        api_client = self.make_api_client()
        response = self.post_deduplicar(api_client, payload=[])

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])

    def test_given_new_processo_when_post_deduplicar_then_create_and_return_resumo(self) -> None:
        api_client = self.make_api_client()
        payload = [ProcessoPayloadBuilder().build()]

        response = self.post_deduplicar(api_client, payload=payload)
        data = response.json()

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)
        self.assertEqual(set(data[0].keys()), {"numero_processo", "grau"})
        self.assertTrue(any(item["numero_processo"] == PROCESSO_NUMERO_1 for item in data))
        self.assertEqual(set(data[0].keys()), RESUMO_RESPONSE_KEYS)
        self.assertEqual(Processo.objects.count(), 1)

    def test_given_existing_with_same_timestamp_when_post_deduplicar_then_filter_out(self) -> None:
        api_client = self.make_api_client()
        DataSetup.create_processo_existente(
            numero_processo=PROCESSO_NUMERO_1,
            data_hora_ultima_atualizacao=DATA_BASE,
        )
        payload = [ProcessoPayloadBuilder().with_data_atualizacao(DATA_BASE).build()]

        response = self.post_deduplicar(api_client, payload=payload)

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])
        self.assertEqual(Processo.objects.count(), 1)

    def test_given_existing_with_older_timestamp_when_post_deduplicar_then_create_new_entry(self) -> None:
        api_client = self.make_api_client()
        DataSetup.create_processo_existente(
            numero_processo=PROCESSO_NUMERO_1,
            data_hora_ultima_atualizacao=DATA_BASE,
            tribunal="TRT6",
            grau="G2",
        )
        payload = [
            ProcessoPayloadBuilder()
            .with_numero_processo(PROCESSO_NUMERO_1)
            .with_data_atualizacao(DATA_NOVA)
            .build()
        ]

        response = self.post_deduplicar(api_client, payload=payload)
        data = response.json()

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)
        self.assertTrue(any(item["numero_processo"] == PROCESSO_NUMERO_1 for item in data))
        self.assertEqual(
            Processo.objects.filter(
                numero_processo=PROCESSO_NUMERO_1,
                tribunal="TRT6",
                grau="G1",
            ).count(),
            1,
        )

    def test_given_existing_with_null_timestamp_when_input_has_timestamp_then_include_in_response(self) -> None:
        api_client = self.make_api_client()
        DataSetup.create_processo_existente(
            numero_processo=PROCESSO_NUMERO_1,
            data_hora_ultima_atualizacao=None,
            tribunal="TRT6",
            grau="G2",
        )
        payload = [ProcessoPayloadBuilder().with_data_atualizacao(DATA_BASE).build()]

        response = self.post_deduplicar(api_client, payload=payload)
        data = response.json()

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)
        self.assertTrue(any(item["numero_processo"] == PROCESSO_NUMERO_1 for item in data))

    def test_given_existing_same_unique_key_with_newer_timestamp_when_post_deduplicar_then_filter_out(self) -> None:
        api_client = self.make_api_client()
        DataSetup.create_processo_existente(
            numero_processo=PROCESSO_NUMERO_1,
            data_hora_ultima_atualizacao=DATA_BASE,
            tribunal="TRT6",
            grau="G1",
        )
        payload = [
            ProcessoPayloadBuilder()
            .with_numero_processo(PROCESSO_NUMERO_1)
            .with_data_atualizacao(DATA_NOVA)
            .build()
        ]

        response = self.post_deduplicar(api_client, payload=payload)

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])
        self.assertEqual(
            Processo.objects.filter(
                numero_processo=PROCESSO_NUMERO_1,
                tribunal="TRT6",
                grau="G1",
            ).count(),
            1,
        )

    def test_given_invalid_payload_when_post_deduplicar_then_return_400(self) -> None:
        api_client = self.make_api_client()
        payload = [{"tribunal": "TRT6", "grau": "G1"}]

        response = api_client.post(DEDUPLICAR_ENDPOINT, payload, format="json")

        self.assert_response_fail(response, status.HTTP_400_BAD_REQUEST)
        body = response.json()
        self.assertIsInstance(body, list)
        self.assertIn("numero_processo", body[0])

    def test_given_duplicate_items_in_same_request_when_post_deduplicar_then_deduplicate_and_create_once(self) -> None:
        api_client = self.make_api_client()
        payload_item = ProcessoPayloadBuilder().build()
        payload = [payload_item, payload_item]

        response = self.post_deduplicar(api_client, payload=payload)

        self.assert_response_success(response, status.HTTP_200_OK)
        self.assertEqual(
            Processo.objects.filter(
                numero_processo=PROCESSO_NUMERO_1,
                tribunal="TRT6",
                grau="G1",
            ).count(),
            1,
        )

    def test_given_nested_relations_when_post_deduplicar_then_persist_related_entities(self) -> None:
        api_client = self.make_api_client()
        payload = [
            ProcessoPayloadBuilder()
            .with_numero_processo(PROCESSO_NUMERO_2)
            .with_classe(codigo="CL123", nome="Classe Especial")
            .with_orgao_julgador(codigo=987, nome="Orgao TRT6", codigo_municipio_ibge=2611606)
            .with_assuntos([
                {"codigo": 3001, "nome": "Assunto A"},
                {"codigo": 3002, "nome": "Assunto B"},
            ])
            .build()
        ]

        response = self.post_deduplicar(api_client, payload=payload)

        self.assert_response_success(response, status.HTTP_200_OK)
        processo = Processo.objects.get(numero_processo=PROCESSO_NUMERO_2)
        self.assertTrue(Classe.objects.filter(codigo="CL123").exists())
        self.assertTrue(OrgaoJulgador.objects.filter(codigo=987).exists())
        self.assertTrue(Assunto.objects.filter(codigo=3001).exists())
        self.assertTrue(Assunto.objects.filter(codigo=3002).exists())
        self.assertEqual(processo.assuntos.count(), 2)

    def test_given_integrity_error_mid_batch_when_post_deduplicar_then_transaction_rolls_back(self) -> None:
        api_client = self.make_api_client()
        payload = [
            ProcessoPayloadBuilder().with_numero_processo(PROCESSO_NUMERO_1).build(),
            ProcessoPayloadBuilder().with_numero_processo(PROCESSO_NUMERO_2).build(),
        ]

        call_count = {"value": 0}

        def create_with_failure(serializer_self, validated_data):
            call_count["value"] += 1
            if call_count["value"] == 2:
                raise IntegrityError("forced integrity error")
            return Processo.objects.create(**validated_data)

        with patch("core.views.ProcessoSerializer.create", new=create_with_failure):
            response = self.post_deduplicar(api_client, payload=payload)

        self.assert_response_fail(response, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Processo.objects.count(), 0)
