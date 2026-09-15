
from rest_framework import serializers
from shared.schemas.resumo_ia import Desfecho, ResultadoReclamante, StatusProcesso, TipoAtoPrincipal

from core.models.analise import Analise
from core.models.assunto import Assunto
from core.models.classe import Classe
from core.models.orgao_julgador import OrgaoJulgador
from core.models.palavra_chave import PalavraChave
from core.models.processo import Processo
from core.serializers.analise_serializer import AnaliseSerializer
from core.serializers.assunto_serializer import AssuntoSerializer
from core.serializers.classe_serializer import ClasseSerializer
from core.serializers.fields import BRLDecimalField
from core.serializers.orgao_julgador_serializer import OrgaoJulgadorSerializer
from core.types.processo_dict import ProcessoDict


class ProcessoResumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Processo
        fields = ["numero_processo", "grau"]


class ProcessoSemPdfResumoSerializer(serializers.ModelSerializer):
    grau = serializers.SerializerMethodField()

    class Meta:
        model = Processo
        fields = ["numero_processo", "grau"]

    def get_grau(self, obj: Processo) -> str:
        raw = (obj.grau or "").strip().upper()
        if raw.startswith("G") and len(raw) > 1:
            return raw[1:]
        return raw


class ProcessoSerializer(serializers.ModelSerializer):
    classe = ClasseSerializer(required=False, allow_null=True)
    orgao_julgador = OrgaoJulgadorSerializer(required=False, allow_null=True)
    assuntos = AssuntoSerializer(many=True, required=False)
    analise = AnaliseSerializer(required=False, allow_null=True)

    class Meta:
        model = Processo
        fields = [
            "id",
            "numero_processo",
            "classe",
            "tribunal",
            "data_hora_ultima_atualizacao",
            "grau",
            "data_ajuizamento",
            "orgao_julgador",
            "assuntos",
            "analise",
        ]

    def create(self, validated_data: ProcessoDict):
        if classe_data := validated_data.pop("classe", None):
            classe, _ = Classe.objects.get_or_create(**classe_data)
            validated_data["classe"] = classe

        if orgao_julgador_data := validated_data.pop("orgao_julgador", None):
            orgao_julgador, _ = OrgaoJulgador.objects.get_or_create(**orgao_julgador_data)
            validated_data["orgao_julgador"] = orgao_julgador

        if analise_data := validated_data.pop("analise", None):
            palavras_chave_data = analise_data.pop("palavras_chave", [])
            analise = Analise.objects.create(**analise_data)
            for palavra_data in palavras_chave_data:
                palavra, _ = PalavraChave.objects.get_or_create(**palavra_data)
                analise.palavras_chave.add(palavra)
            validated_data["analise"] = analise

        assuntos_data = validated_data.pop("assuntos", [])
        processo = Processo.objects.create(**validated_data)

        # Handle assuntos
        for assunto_data in assuntos_data:
            assunto, _ = Assunto.objects.get_or_create(**assunto_data)
            processo.assuntos.add(assunto)

        return processo

    def update(self, instance: Processo, validated_data: dict):
        assuntos_data = validated_data.pop("assuntos", [])
        analise_data = validated_data.pop("analise", None)
        orgao_julgador_data = validated_data.pop("orgao_julgador", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Handle orgao_julgador
        if orgao_julgador_data:
            orgao_julgador, _ = OrgaoJulgador.objects.get_or_create(**orgao_julgador_data)
            instance.orgao_julgador = orgao_julgador

        # Handle analise
        if analise_data:
            palavras_chave_data = analise_data.pop("palavras_chave", [])
            if instance.analise:
                for attr, value in analise_data.items():
                    setattr(instance.analise, attr, value)
                instance.analise.save()
            else:
                instance.analise = Analise.objects.create(**analise_data)
            if palavras_chave_data:
                instance.analise.palavras_chave.clear()
                for palavra_data in palavras_chave_data:
                    palavra, _ = PalavraChave.objects.get_or_create(**palavra_data)
                    instance.analise.palavras_chave.add(palavra)

        instance.save()

        # Handle assuntos
        if assuntos_data:
            instance.assuntos.clear()
            for assunto_data in assuntos_data:
                assunto, _ = Assunto.objects.get_or_create(**assunto_data)
                instance.assuntos.add(assunto)

        return instance


class ProcessoDetalheSerializer(ProcessoSerializer):
    movimentos = serializers.JSONField(read_only=True)
    em_andamento = serializers.SerializerMethodField()

    class Meta(ProcessoSerializer.Meta):
        fields = ProcessoSerializer.Meta.fields + ["movimentos", "em_andamento"]

    def get_em_andamento(self, obj: Processo) -> bool:
        if obj.analise is None:
            return True
        return getattr(obj.analise, "status", None) == StatusProcesso.EM_ANDAMENTO


class ProcessoDeduplicarEntradaSerializer(ProcessoSerializer):
    class Meta(ProcessoSerializer.Meta):
        validators = []


class AnaliseEntradaSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if data and isinstance(data, dict):
            status_val = data.get("status")
            if status_val == "arquivado_sem_decisao":
                data = data.copy()
                data["status"] = "arquivado"
        return super().to_internal_value(data)

    resumo = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=1024)
    tipo_ato_principal = serializers.ChoiceField(
        required=False,
        allow_null=True,
        choices=TipoAtoPrincipal.choices(),
    )
    decisao = serializers.CharField(required=False, allow_null=True, allow_blank=True, max_length=1024)
    palavras_chave = serializers.ListField(
        required=False,
        allow_empty=True,
        child=serializers.CharField(max_length=128),
    )
    status = serializers.ChoiceField(required=False, allow_null=True, choices=StatusProcesso.choices())
    desfecho = serializers.ChoiceField(required=False, allow_null=True, choices=Desfecho.choices())
    resultado_reclamante = serializers.ChoiceField(
        required=False,
        allow_null=True,
        choices=ResultadoReclamante.choices(),
    )
    valor_causa = BRLDecimalField(required=False, allow_null=True, max_digits=10, decimal_places=2)
    custas_valor_total = BRLDecimalField(
        required=False,
        allow_null=True,
        max_digits=10,
        decimal_places=2,
    )


class ProcessoAdicionarAnaliseEntradaSerializer(serializers.Serializer):
    numero_processo = serializers.CharField()
    grau = serializers.CharField()
    analise = AnaliseEntradaSerializer()


