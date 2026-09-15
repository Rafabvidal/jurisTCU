from rest_framework import serializers

from core.models.palavra_chave import PalavraChave


class PalavraChaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = PalavraChave
        fields = ["id", "nome"]
