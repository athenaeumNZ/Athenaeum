# Generated by Django 4.1.4 on 2023-01-06 03:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vinylLibrary', '0005_alter_libraryplate_cover_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='librarycrate',
            name='date_modified',
            field=models.DateField(auto_now=True),
        ),
    ]
