# Generated by Django 4.1.4 on 2023-01-16 10:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('musicDatabase', '0022_alter_vinyltrack_vibe'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vinylrelease',
            name='check_release_date',
        ),
        migrations.RemoveField(
            model_name='vinylrelease',
            name='label_profile',
        ),
        migrations.RemoveField(
            model_name='vinylrelease',
            name='release_date_inaccurate',
        ),
    ]