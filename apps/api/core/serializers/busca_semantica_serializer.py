from rest_framework import serializers

from core.serializers.processo_serializer import ProcessoSerializer


class BuscaSemanticaEntradaSerializer(serializers.Serializer):
    """Valida o payload de entrada para a busca semântica."""

    consulta = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={"required": "O campo 'consulta' é obrigatório.", "blank": "A consulta não pode estar vazia."},
    )
    top_k = serializers.IntegerField(required=False, default=5, min_value=1, max_value=50)
    metrica = serializers.ChoiceField(
        choices=["cosseno", "euclidiana", "manhattan", "jaccard", "levenshtein"],
        required=False,
        default="cosseno",
    )


class ProcessoBuscaSemanticaSaidaSerializer(ProcessoSerializer):
    """Serializa o resultado da busca semântica, estendendo o ProcessoSerializer com a similaridade."""

    similaridade = serializers.FloatField(read_only=True)

    class Meta(ProcessoSerializer.Meta):
        fields = ProcessoSerializer.Meta.fields + ["similaridade"]
