# Generated by Django 4.1.4 on 2023-01-13 03:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinylLibrary', '0013_alter_libraryplate_vinyl_color'),
    ]

    operations = [
        migrations.RenameField(
            model_name='libraryplate',
            old_name='vinyl_color',
            new_name='vinyl_colour',
        ),
    ]
