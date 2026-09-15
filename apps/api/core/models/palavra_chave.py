from django.db import models


class PalavraChave(models.Model):
    nome = models.CharField(max_length=128)

    def __str__(self) -> str:
        return self.nome
