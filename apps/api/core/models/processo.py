
import json
import zlib
from django.db import models

from core.models.analise import Analise
from core.models.assunto import Assunto
from core.models.classe import Classe
from core.models.orgao_julgador import OrgaoJulgador


class CompressedJSONField(models.BinaryField):
    """
    A custom field that serializes Python objects (lists/dicts) to JSON,
    compresses them with zlib, and stores the resulting bytes in a BinaryField.
    It transparently decompresses and deserializes the value when read.
    """
    description = "Compressed JSON Field"

    def __init__(self, *args, **kwargs):
        kwargs['editable'] = True
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['editable']
        return name, path, args, kwargs

    def get_prep_value(self, value):
        if value is None:
            return None
        if isinstance(value, (bytes, memoryview)):
            return bytes(value)
        serialized = json.dumps(value, ensure_ascii=False)
        return zlib.compress(serialized.encode('utf-8'))

    def from_db_value(self, value, expression, connection):
        if value is None:
            return []
        if isinstance(value, (bytes, memoryview)):
            try:
                decompressed = zlib.decompress(bytes(value))
                return json.loads(decompressed.decode('utf-8'))
            except Exception:
                return []
        return value

    def to_python(self, value):
        if value is None:
            return []
        if isinstance(value, (bytes, memoryview)):
            try:
                decompressed = zlib.decompress(bytes(value))
                return json.loads(decompressed.decode('utf-8'))
            except Exception:
                return []
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                return []
        return value

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return json.dumps(self.to_python(value), ensure_ascii=False)


class Processo(models.Model):
    numero_processo = models.CharField(max_length=20, blank=False)
    classe = models.ForeignKey(Classe, on_delete=models.SET_NULL, blank=True, null=True)
    tribunal = models.CharField(max_length=32, blank=True)
    data_hora_ultima_atualizacao = models.DateField(blank=True, null=True)
    grau = models.CharField(max_length=32, blank=True) #G1 ou G2
    data_ajuizamento = models.DateField(blank=True, null=True)
    pdf_url = models.URLField(blank=True, null=True)
    pdf_sha256 = models.CharField(max_length=64, blank=True, null=True)
    movimentos = CompressedJSONField(default=list, blank=True)
    orgao_julgador = models.ForeignKey(OrgaoJulgador, on_delete=models.SET_NULL, blank=True, null=True)
    assuntos = models.ManyToManyField(Assunto, blank=True, default=list)
    analise = models.OneToOneField(Analise, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["numero_processo", "tribunal", "grau"],
                name="uniq_datajud_numero_tribunal_grau",
            )
        ]


    def __str__(self) -> str:
        return self.numero_processo
