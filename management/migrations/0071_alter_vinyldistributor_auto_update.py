# Generated by Django 4.1.4 on 2023-10-14 01:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0070_vinyldistributor_auto_update'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vinyldistributor',
            name='auto_update',
            field=models.BooleanField(default=False),
        ),
    ]
