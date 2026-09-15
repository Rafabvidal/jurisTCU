from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase


class TestMinioCleanupCommand(TestCase):
    @patch("shared.minio_cleanup.get_s3_client")
    def test_limpar_minio_pdfs_invalidos_command(self, mock_get_s3_client):
        class DummyClient:
            def __init__(self):
                self.deleted = []

            def list_objects(self, bucket):
                from collections import namedtuple

                Obj = namedtuple('Obj', 'object_name')
                return [Obj('1000_1.pdf'), Obj('arquivo.tmp'), Obj('1000_1.pdf')]

            def delete_object(self, bucket, name):
                self.deleted.append(name)

        dummy_client = DummyClient()
        mock_get_s3_client.return_value = dummy_client

        call_command('limpar_minio_pdfs_invalidos', verbosity=0)

        self.assertIn('arquivo.tmp', dummy_client.deleted)
        self.assertEqual(dummy_client.deleted.count('1000_1.pdf'), 1)
