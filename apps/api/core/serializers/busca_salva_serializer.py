from rest_framework import serializers

from core.models.busca_salva import BuscaSalva


class BuscaSalvaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuscaSalva
        fields = ['id', 'title', 'query', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
