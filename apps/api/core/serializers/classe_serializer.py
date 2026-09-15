from rest_framework import serializers

from core.models.classe import Classe


class ClasseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classe
        fields = ["codigo", "nome"]
