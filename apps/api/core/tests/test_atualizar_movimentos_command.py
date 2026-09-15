import json
import zlib
from unittest.mock import patch

from django.core.management import call_command
from django.db import connection
from django.test import TestCase

from core.tests.helpers import DataSetup


class TestAtualizarMovimentosCommand(TestCase):
    @patch("requests.post")
    def test_atualizar_movimentos_command(self, mock_post):
        # 1. Create a dummy process
        processo = DataSetup.create_processo_existente(
            numero_processo="00001234520255060001",
            data_hora_ultima_atualizacao=None,
            grau="G1"
        )
        self.assertFalse(processo.movimentos)  # should be empty initially

        # 2. Mock requests.post to return DataJud API hits
        class DummyResponse:
            def __init__(self):
                self.ok = True
                self.status_code = 200

            def json(self):
                return {
                    "hits": {
                        "hits": [
                            {
                                "_source": {
                                    "numeroProcesso": "00001234520255060001",
                                    "grau": "1",
                                    "movimentos": [
                                        {
                                            "codigo": 12,
                                            "nome": "Audiência Realizada",
                                            "dataHora": "2025-05-20T10:00:00Z",
                                            "orgaoJulgador": {
                                                "codigo": 1001,
                                                "nome": "1ª Vara do Trabalho"
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }

        mock_post.return_value = DummyResponse()

        # 3. Call the management command
        call_command("atualizar_movimentos")

        # 4. Reload from database and assert
        processo.refresh_from_db()

        # Assert movements are correctly uncompressed and returned as python list
        self.assertEqual(len(processo.movimentos), 1)
        mov = processo.movimentos[0]
        self.assertEqual(mov["codigo"], 12)
        self.assertEqual(mov["nome"], "Audiência Realizada")
        self.assertEqual(mov["data_hora"], "2025-05-20T10:00:00Z")
        self.assertEqual(mov["orgao_julgador"]["codigo"], 1001)
        self.assertEqual(mov["orgao_julgador"]["nome"], "1ª Vara do Trabalho")

        # Assert that they are stored as compressed bytes in the database
        # Let's bypass Django field converters using a raw connection cursor
        with connection.cursor() as cursor:
            cursor.execute("SELECT movimentos FROM core_processo WHERE id = %s", [processo.id])
            raw_db_val = cursor.fetchone()[0]

        self.assertIsInstance(raw_db_val, (bytes, memoryview))

        # Check that decompressing it yields the original JSON string
        decompressed = zlib.decompress(bytes(raw_db_val))
        parsed = json.loads(decompressed.decode("utf-8"))
        self.assertEqual(parsed[0]["nome"], "Audiência Realizada")
