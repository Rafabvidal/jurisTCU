"""Endpoints da API JusTRT6 com controle de acesso RBAC e auditoria de segurança."""

import hashlib

from django.contrib.auth import authenticate
from django.db import IntegrityError, transaction
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from shared.logger import get_logger

logger = get_logger("core.views")

from core.models.audit_log import SecurityAuditLog
from core.models.busca_salva import BuscaSalva
from core.permissions import IsAdminRole
from core.serializers.auth_serializer import (
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)
from core.serializers.busca_salva_serializer import BuscaSalvaSerializer
from core.serializers.busca_semantica_serializer import (
    BuscaSemanticaEntradaSerializer,
    ProcessoBuscaSemanticaSaidaSerializer,
)
from core.serializers.processo_serializer import (
    ProcessoAdicionarAnaliseEntradaSerializer,
    ProcessoDeduplicarEntradaSerializer,
    ProcessoDetalheSerializer,
    ProcessoResumoSerializer,
    ProcessoSemPdfResumoSerializer,
    ProcessoSerializer,
)
from core.services import (
    ProcessoNotFoundError,
    ProcessoSemPdfLookupError,
    adicionar_analise_ao_processo,
    buscar_processos_semanticos,
    filtrar_processos_faltantes,
    listar_processos_nao_possuem_analise,
    listar_processos_nao_possuem_pdf,
    obter_processo_por_numero_grau,
)


def _get_client_ip(request: Request) -> str:
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


class ProcessoViewset(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def deduplicar(self, request: Request):
        input_serializer = ProcessoDeduplicarEntradaSerializer(data=request.data, many=True)
        input_serializer.is_valid(raise_exception=True)

        processos_filtrados = filtrar_processos_faltantes(input_serializer.validated_data)

        try:
            with transaction.atomic():
                created_items = [ProcessoSerializer().create(item) for item in processos_filtrados]
        except IntegrityError as exc:
            raise ValidationError(
                {
                    "mensagem": "Falha ao persistir lote de processos. Nenhum processo foi criado.",
                    "detalhes": str(exc),
                }
            ) from exc

        output_serializer = ProcessoResumoSerializer(created_items, many=True)

        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def nao_possuem_pdf(self, request: Request):
        try:
            processos = listar_processos_nao_possuem_pdf()
        except ProcessoSemPdfLookupError as exc:
            return Response(
                {
                    "mensagem": "Falha ao consultar pendencias de PDF.",
                    "detalhes": str(exc),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        output_serializer = ProcessoSemPdfResumoSerializer(processos, many=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def nao_possuem_analise(self, request: Request):
        processos = listar_processos_nao_possuem_analise()
        output_serializer = ProcessoSemPdfResumoSerializer(processos, many=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def adicionar_analise(self, request: Request):

        input_serializer = ProcessoAdicionarAnaliseEntradaSerializer(data=request.data)

        logger.info("adicionar_analise called: preview=%s", str(request.data))

        is_valid = input_serializer.is_valid(raise_exception=False)
        if not is_valid:
            logger.warning("adicionar_analise payload validation failed: errors=%s", input_serializer.errors)
            raise ValidationError(
                {
                    "mensagem": "Payload de analise invalido.",
                    "detalhes": input_serializer.errors,
                }
            )

        payload = input_serializer.validated_data
        try:
            processo = adicionar_analise_ao_processo(
                numero_processo=payload["numero_processo"],
                grau=payload["grau"],
                analise_data=dict(payload["analise"]),
            )
        except ProcessoNotFoundError as exc:
            return Response(
                {
                    "mensagem": "Processo nao encontrado.",
                    "detalhes": str(exc),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        pdf_sha256 = payload.get("pdf_sha256")
        if pdf_sha256:
            processo.pdf_sha256 = pdf_sha256
            processo.save(update_fields=["pdf_sha256"])

        output_serializer = ProcessoResumoSerializer(processo)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def busca_semantica(self, request: Request):
        input_serializer = BuscaSemanticaEntradaSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        payload = input_serializer.validated_data
        consulta = payload["consulta"]
        top_k = payload.get("top_k", 5)
        metrica = payload.get("metrica", "cosseno")

        try:
            resultados = buscar_processos_semanticos(consulta=consulta, top_k=top_k, metrica=metrica)
        except Exception as exc:
            logger.exception("Falha ao executar busca semântica.")
            return Response(
                {
                    "mensagem": "Erro interno ao executar a busca semântica.",
                    "detalhes": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        output_serializer = ProcessoBuscaSemanticaSaidaSerializer(resultados, many=True)
        return Response({"items": output_serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def detalhe(self, request: Request):
        numero_processo = (request.query_params.get("numero_processo") or "").strip()
        grau = (request.query_params.get("grau") or "").strip()

        if not numero_processo or not grau:
            raise ValidationError(
                {
                    "mensagem": "Parametros obrigatorios ausentes.",
                    "detalhes": {"numero_processo": numero_processo, "grau": grau},
                }
            )

        processo = obter_processo_por_numero_grau(numero_processo=numero_processo, grau=grau)
        if processo is None:
            return Response(
                {
                    "mensagem": "Processo nao encontrado.",
                    "detalhes": {
                        "numero_processo": numero_processo,
                        "grau": grau,
                    },
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        output_serializer = ProcessoDetalheSerializer(processo)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='verificar-integridade')
    def verificar_integridade(self, request: Request):
        """Verifica a integridade de um PDF de processo comparando o SHA-256 armazenado com o atual no S3."""
        from core.models.processo import Processo
        from shared.s3_client import get_s3_client

        numero_processo = (request.query_params.get("numero_processo") or "").strip()
        grau = (request.query_params.get("grau") or "").strip()

        if not numero_processo or not grau:
            raise ValidationError({"mensagem": "Parametros numero_processo e grau sao obrigatorios."})

        processo = obter_processo_por_numero_grau(numero_processo=numero_processo, grau=grau)
        if processo is None:
            return Response({"mensagem": "Processo nao encontrado."}, status=status.HTTP_404_NOT_FOUND)

        if not processo.pdf_sha256:
            return Response(
                {"status": "SEM_HASH", "mensagem": "Processo não possui hash SHA-256 registrado."},
                status=status.HTTP_200_OK,
            )

        client = get_s3_client()
        from core.services import _s3_object_key, _normalize_grau
        object_name = _s3_object_key(numero_processo, grau)

        try:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp_path = tmp.name
            client.get_object("pje-documents", object_name, tmp_path)
            with open(tmp_path, "rb") as f:
                current_hash = hashlib.sha256(f.read()).hexdigest()
            import os
            os.remove(tmp_path)
        except Exception as exc:
            return Response(
                {"status": "ERRO", "mensagem": f"Falha ao baixar PDF do S3: {exc}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        ip = _get_client_ip(request)
        if current_hash == processo.pdf_sha256:
            SecurityAuditLog.log(
                event_type=SecurityAuditLog.EventType.INTEGRITY_OK,
                severity=SecurityAuditLog.Severity.INFO,
                user=request.user if request.user.is_authenticated else None,
                ip_address=ip,
                numero_processo=numero_processo,
                grau=grau,
            )
            return Response({"status": "INTEGRO", "sha256": current_hash}, status=status.HTTP_200_OK)

        SecurityAuditLog.log(
            event_type=SecurityAuditLog.EventType.INTEGRITY_VIOLATION,
            severity=SecurityAuditLog.Severity.CRITICAL,
            user=request.user if request.user.is_authenticated else None,
            ip_address=ip,
            numero_processo=numero_processo,
            grau=grau,
            hash_esperado=processo.pdf_sha256,
            hash_encontrado=current_hash,
        )
        return Response(
            {
                "status": "ADULTERADO",
                "mensagem": "O documento foi adulterado! O hash não confere.",
                "hash_esperado": processo.pdf_sha256,
                "hash_encontrado": current_hash,
            },
            status=status.HTTP_409_CONFLICT,
        )


def _auth_payload(user, token: Token) -> dict:
    """Resposta padrao apos login/registro: token + dados do usuario."""
    return {
        "token": token.key,
        "user": UserSerializer(user).data,
    }


class RegisterView(APIView):
    """POST /api/auth/register/ — cria o usuario (username=email) e ja devolve o token."""

    authentication_classes: list = []
    permission_classes: list = []

    def post(self, request: Request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        SecurityAuditLog.log(
            event_type=SecurityAuditLog.EventType.LOGIN_SUCCESS,
            severity=SecurityAuditLog.Severity.INFO,
            user=user,
            ip_address=_get_client_ip(request),
            action="register",
        )
        return Response(_auth_payload(user, token), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """POST /api/auth/login/ — autentica por email/senha e devolve o token."""

    authentication_classes: list = []
    permission_classes: list = []

    def post(self, request: Request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        user = authenticate(request, username=email, password=password)

        ip = _get_client_ip(request)

        if user is None:
            SecurityAuditLog.log(
                event_type=SecurityAuditLog.EventType.LOGIN_FAILED,
                severity=SecurityAuditLog.Severity.WARNING,
                ip_address=ip,
                email=email,
            )
            return Response(
                {"mensagem": "E-mail ou senha invalidos."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token, _ = Token.objects.get_or_create(user=user)
        SecurityAuditLog.log(
            event_type=SecurityAuditLog.EventType.LOGIN_SUCCESS,
            severity=SecurityAuditLog.Severity.INFO,
            user=user,
            ip_address=ip,
        )
        return Response(_auth_payload(user, token), status=status.HTTP_200_OK)


class LogoutView(APIView):
    """POST /api/auth/logout/ — revoga o token ativo do usuario."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        SecurityAuditLog.log(
            event_type=SecurityAuditLog.EventType.LOGOUT,
            severity=SecurityAuditLog.Severity.INFO,
            user=request.user,
            ip_address=_get_client_ip(request),
        )
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserMeView(APIView):
    """GET /api/auth/me/ — perfil do usuario logado."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)

    def patch(self, request: Request):
        user = request.user
        name = request.data.get('name')
        if name is not None:
            user.first_name = name
            user.save()
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)


class SavedSearchViewSet(viewsets.ModelViewSet):
    """CRUD das buscas salvas, restrito ao usuario autenticado."""

    serializer_class = BuscaSalvaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.buscas_salvas.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ────────────────────────────────────────────────────────────────────
# Endpoints administrativos (RBAC — somente is_staff=True)
# ────────────────────────────────────────────────────────────────────

class AdminAuditLogView(APIView):
    """GET /api/admin/audit-logs/ — lista eventos de auditoria de segurança (somente admin)."""

    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request: Request):
        from rest_framework import serializers as drf_serializers

        class AuditLogSerializer(drf_serializers.ModelSerializer):
            username = drf_serializers.CharField(source="user.username", default=None)
            detail = drf_serializers.SerializerMethodField()

            class Meta:
                model = SecurityAuditLog
                fields = ["id", "timestamp", "username", "ip_address", "event_type", "severity", "detail"]

            def get_detail(self, obj):
                return obj.get_decrypted_detail()

        limit = min(int(request.query_params.get("limit", 100)), 500)
        event_type = request.query_params.get("event_type")

        qs = SecurityAuditLog.objects.select_related("user").all()
        if event_type:
            qs = qs.filter(event_type=event_type)

        logs = qs[:limit]
        serializer = AuditLogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminReindexView(APIView):
    """POST /api/admin/reindexar/ — dispara reindexação vetorial (somente admin)."""

    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request: Request):
        from core.services import reindexar_processos_sem_embedding
        count = reindexar_processos_sem_embedding()
        return Response({"mensagem": f"{count} processos reindexados."}, status=status.HTTP_200_OK)

