# Generated by Django 4.1.4 on 2023-08-14 23:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('musicDatabase', '0067_vinylrelease_most_common'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vinylrelease',
            name='finalized',
        ),
        migrations.RemoveField(
            model_name='vinylrelease',
            name='is_bundle',
        ),
        migrations.RemoveField(
            model_name='vinylrelease',
            name='no_mark_up_price_NZ',
        ),
    ]
