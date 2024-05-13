# Generated by Django 4.1.4 on 2023-01-05 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0003_alter_crate_crate_energy_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crate',
            name='crate_energy_level',
            field=models.CharField(choices=[('-', '-'), ('one', '1'), ('two', '2'), ('three', '3'), ('four', '4'), ('five', '5'), ('six', '6')], default='1', max_length=20),
        ),
    ]
