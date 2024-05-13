# Generated by Django 4.1.4 on 2023-01-21 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicDatabase', '0028_vinyltrack_key_in'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vinyltrack',
            name='energy_level',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='vinyltrack',
            name='genre',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='vinyltrack',
            name='vibe',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]