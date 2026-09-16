import json
import logging

from django.conf import settings
from django.db import models

logger = logging.getLogger(__name__)


class SecurityAuditLog(models.Model):
    class EventType(models.TextChoices):
        LOGIN_SUCCESS = "LOGIN_SUCCESS"
        LOGIN_FAILED = "LOGIN_FAILED"
        ACCESS_DENIED = "ACCESS_DENIED"
        INTEGRITY_VIOLATION = "INTEGRITY_VIOLATION"
        INTEGRITY_OK = "INTEGRITY_OK"
        PROMPT_INJECTION_DETECTED = "PROMPT_INJECTION_DETECTED"
        DATA_EXPORT = "DATA_EXPORT"
        PRIVILEGE_CHANGE = "PRIVILEGE_CHANGE"
        LOGOUT = "LOGOUT"

    class Severity(models.TextChoices):
        INFO = "INFO"
        WARNING = "WARNING"
        CRITICAL = "CRITICAL"

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    event_type = models.CharField(max_length=40, choices=EventType.choices, db_index=True)
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.INFO)
    detail = models.TextField(default="", blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"[{self.severity}] {self.event_type} @ {self.timestamp}"

    @classmethod
    def _encrypt_detail(cls, data: dict) -> str:
        """Cifra o dicionário de detalhes com Fernet (AES) antes de persistir."""
        from shared.encryption import encrypt
        return encrypt(json.dumps(data, ensure_ascii=False, default=str))

    @classmethod
    def _decrypt_detail(cls, token: str) -> dict:
        """Decifra o campo detail armazenado e retorna o dicionário original."""
        from shared.encryption import decrypt
        return json.loads(decrypt(token))

    def get_decrypted_detail(self) -> dict:
        """Retorna o detail decifrado. Se falhar (chave errada, dado legado), retorna o valor bruto."""
        if not self.detail:
            return {}
        try:
            return self._decrypt_detail(self.detail)
        except Exception:
            try:
                return json.loads(self.detail) if isinstance(self.detail, str) else self.detail
            except (json.JSONDecodeError, TypeError):
                return {"_raw": self.detail}

    @classmethod
    def log(cls, event_type: str, severity: str = "INFO", user=None, ip_address: str | None = None, **extra):
        try:
            encrypted = cls._encrypt_detail(extra)
        except Exception:
            logger.warning("ENCRYPTION_KEY não configurada — audit log salvo sem criptografia.")
            encrypted = json.dumps(extra, ensure_ascii=False, default=str)
        return cls.objects.create(
            event_type=event_type,
            severity=severity,
            user=user,
            ip_address=ip_address,
            detail=encrypted,
        )
