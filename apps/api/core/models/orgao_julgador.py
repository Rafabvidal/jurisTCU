from django.db import models


class OrgaoJulgador(models.Model):
    codigo_municipio_ibge = models.IntegerField(blank=True, null=True)
    codigo = models.IntegerField()
    nome = models.CharField(max_length=128)

    def __str__(self) -> str:
        return self.nome
