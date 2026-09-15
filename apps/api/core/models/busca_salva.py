from django.contrib.auth.models import User
from django.db import models

from core.models.processo import CompressedJSONField


class BuscaSalva(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buscas_salvas')
    title = models.CharField(max_length=150)
    query = models.TextField()
    # Lista comprimida (zlib) dos numero_processo ja vistos, usada pelo search-notifier
    # para detectar novos resultados sem disparar notificacoes duplicadas.
    last_results = CompressedJSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Busca Salva'
        verbose_name_plural = 'Buscas Salvas'

    def __str__(self) -> str:
        return f"{self.title} ({self.user.email})"
