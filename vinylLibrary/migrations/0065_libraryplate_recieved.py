# Generated by Django 4.1.4 on 2023-04-08 03:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vinylLibrary', '0064_alter_libraryplate_release_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='libraryplate',
            name='recieved',
            field=models.BooleanField(default=False),
        ),
    ]