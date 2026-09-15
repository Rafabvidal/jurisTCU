import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0008_buscasalva_last_results'),
    ]

    operations = [
        migrations.AddField(
            model_name='processo',
            name='pdf_sha256',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.CreateModel(
            name='SecurityAuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('event_type', models.CharField(
                    choices=[
                        ('LOGIN_SUCCESS', 'Login Success'),
                        ('LOGIN_FAILED', 'Login Failed'),
                        ('ACCESS_DENIED', 'Access Denied'),
                        ('INTEGRITY_VIOLATION', 'Integrity Violation'),
                        ('INTEGRITY_OK', 'Integrity Ok'),
                        ('PROMPT_INJECTION_DETECTED', 'Prompt Injection Detected'),
                        ('DATA_EXPORT', 'Data Export'),
                        ('PRIVILEGE_CHANGE', 'Privilege Change'),
                        ('LOGOUT', 'Logout'),
                    ],
                    db_index=True,
                    max_length=40,
                )),
                ('severity', models.CharField(
                    choices=[('INFO', 'Info'), ('WARNING', 'Warning'), ('CRITICAL', 'Critical')],
                    default='INFO',
                    max_length=10,
                )),
                ('detail', models.JSONField(blank=True, default=dict)),
                ('user', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='audit_logs',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]
