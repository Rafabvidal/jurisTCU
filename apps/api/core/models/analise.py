from django.db import models
from pgvector.django import VectorField
from shared.schemas.resumo_ia import Desfecho, ResultadoReclamante, StatusProcesso, TipoAtoPrincipal

from core.models.palavra_chave import PalavraChave


class Analise(models.Model):
    resumo = models.CharField(max_length=1024, blank=True)
    tipo_ato_principal= models.CharField(choices=TipoAtoPrincipal.choices(), max_length=32, blank=True)
    decisao = models.CharField(max_length=1024, blank=True)

    # Juntado com palavras_chave_desfecho
    palavras_chave = models.ManyToManyField(PalavraChave, blank=True, default=list)

    status = models.CharField(choices=StatusProcesso.choices(), max_length=32, blank=True)
    desfecho = models.CharField(choices=Desfecho.choices(), max_length=32, blank=True)
    resultado_reclamante = models.CharField(choices=ResultadoReclamante.choices(), max_length=32, blank=True)

    # É possível calcular as custas percentuais a partir desses dois
    valor_causa = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    custas_valor_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Vetor de embedding de 384 dimensões para busca semântica
    embedding = VectorField(dimensions=384, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.resumo[:50]}..."
