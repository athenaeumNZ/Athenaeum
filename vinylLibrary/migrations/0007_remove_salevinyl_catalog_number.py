# Generated by Django 4.1.4 on 2023-01-12 05:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinylLibrary', '0006_librarycrate_date_modified'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='salevinyl',
            name='catalog_number',
        ),
    ]