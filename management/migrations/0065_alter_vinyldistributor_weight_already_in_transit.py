# Generated by Django 4.1.4 on 2023-03-24 02:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0064_vinyldistributor_weight_already_in_transit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vinyldistributor',
            name='weight_already_in_transit',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]