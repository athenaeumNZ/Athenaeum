# Generated by Django 4.1.4 on 2023-02-20 00:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinylLibrary', '0060_remove_wantlistplate_related_vinyl_plate_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='libraryplate',
            name='vinyl_colour',
        ),
    ]