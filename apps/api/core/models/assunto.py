from django.db import models


class Assunto(models.Model):
    codigo = models.IntegerField()
    nome = models.CharField(max_length=128)

    def __str__(self) -> str:
        return self.nome
