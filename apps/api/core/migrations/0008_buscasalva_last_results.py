# Generated for BuscaSalva.last_results (CompressedJSONField).

import core.models.processo
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_buscasalva'),
    ]

    operations = [
        migrations.AddField(
            model_name='buscasalva',
            name='last_results',
            field=core.models.processo.CompressedJSONField(blank=True, default=list),
        ),
    ]
