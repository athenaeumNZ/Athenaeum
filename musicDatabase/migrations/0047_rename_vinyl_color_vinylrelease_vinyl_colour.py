# Generated by Django 4.1.4 on 2023-02-19 23:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('musicDatabase', '0046_vinylrelease_release_type_vinylrelease_sleeve_type_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vinylrelease',
            old_name='vinyl_color',
            new_name='vinyl_colour',
        ),
    ]
