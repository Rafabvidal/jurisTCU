
from django.db import models


class Classe(models .Model):
    codigo = models.CharField(max_length=20, blank=False)
    nome = models.CharField(max_length=128, blank=True)

    def __str__(self) -> str:
        return self.nome
