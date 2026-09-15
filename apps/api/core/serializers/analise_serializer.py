from rest_framework import serializers

from core.models.analise import Analise
from core.serializers.palavras_chave_serializer import PalavraChaveSerializer


class AnaliseSerializer(serializers.ModelSerializer):
    palavras_chave = PalavraChaveSerializer(many=True, read_only=True)

    class Meta:
        model = Analise
        fields = [
            "id",
            "resumo",
            "tipo_ato_principal",
            "decisao",
            "palavras_chave",
            "status",
            "desfecho",
            "resultado_reclamante",
            "valor_causa",
            "custas_valor_total",
        ]
