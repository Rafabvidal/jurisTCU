from django.conf import settings
from django.db import models


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
    detail = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return f"[{self.severity}] {self.event_type} @ {self.timestamp}"

    @classmethod
    def log(cls, event_type: str, severity: str = "INFO", user=None, ip_address: str | None = None, **extra):
        return cls.objects.create(
            event_type=event_type,
            severity=severity,
            user=user,
            ip_address=ip_address,
            detail=extra,
        )
