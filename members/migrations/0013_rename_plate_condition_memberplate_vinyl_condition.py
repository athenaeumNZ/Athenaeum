# Generated by Django 4.1.4 on 2023-12-29 02:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0012_memberplate_memberrelease_memberreleasestatuschoices_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='memberplate',
            old_name='plate_condition',
            new_name='vinyl_condition',
        ),
    ]
