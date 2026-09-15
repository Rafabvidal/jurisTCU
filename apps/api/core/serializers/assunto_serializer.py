from rest_framework import serializers

from core.models.assunto import Assunto


class AssuntoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assunto
        fields = ["id", "codigo", "nome"]
