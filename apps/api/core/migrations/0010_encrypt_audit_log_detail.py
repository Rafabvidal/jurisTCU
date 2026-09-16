from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_security_features'),
    ]

    operations = [
        migrations.AlterField(
            model_name='securityauditlog',
            name='detail',
            field=models.TextField(blank=True, default=''),
        ),
    ]
