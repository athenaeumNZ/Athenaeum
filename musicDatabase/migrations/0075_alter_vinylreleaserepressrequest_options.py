# Generated by Django 4.1.4 on 2023-12-22 23:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('musicDatabase', '0074_vinylreleaserepressrequest'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vinylreleaserepressrequest',
            options={'ordering': ['vinyl_release', 'added']},
        ),
    ]
