# Generated for BuscaSalva model.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0006_alter_processo_movimentos'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuscaSalva',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('query', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buscas_salvas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Busca Salva',
                'verbose_name_plural': 'Buscas Salvas',
                'ordering': ['-updated_at'],
            },
        ),
    ]
