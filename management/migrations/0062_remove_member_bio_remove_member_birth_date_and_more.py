# Generated by Django 4.1.4 on 2023-03-21 00:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0061_vinyldistributor_distributor_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='member',
            name='bio',
        ),
        migrations.RemoveField(
            model_name='member',
            name='birth_date',
        ),
        migrations.RemoveField(
            model_name='member',
            name='gender',
        ),
    ]
