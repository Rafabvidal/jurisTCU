from rest_framework import serializers

from core.models.orgao_julgador import OrgaoJulgador


class OrgaoJulgadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgaoJulgador
        fields = ["id", "codigo_municipio_ibge", "codigo", "nome"]
