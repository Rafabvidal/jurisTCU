def test_deduplicate_processos(monkeypatch):
    import importlib.util
    import pathlib

    dedup_path = pathlib.Path(__file__).resolve().parents[2] / 'deduplication.py'
    spec = importlib.util.spec_from_file_location('deduplication', dedup_path)
    dedup = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dedup)
    deduplicate_processos = dedup.deduplicate_processos

    class DummyClient:
        def __init__(self):
            self.deleted = []

        def list_objects(self, bucket):
            from collections import namedtuple

            Obj = namedtuple('Obj', 'object_name')
            return [
                Obj('0001_1.pdf'),
                Obj('arquivo-temporario.pdf'),
                Obj('0001_1.pdf'),
                Obj('0002_2.pdf'),
                Obj('nota.txt'),
            ]

        def delete_object(self, bucket, name):
            self.deleted.append(name)

    dummy_client = DummyClient()
    monkeypatch.setattr('shared.minio_cleanup.get_s3_client', lambda: dummy_client)

    result = deduplicate_processos()

    assert result['removed'] == 3
    assert 'arquivo-temporario.pdf' in dummy_client.deleted
    assert 'nota.txt' in dummy_client.deleted
    assert dummy_client.deleted.count('0001_1.pdf') == 1
