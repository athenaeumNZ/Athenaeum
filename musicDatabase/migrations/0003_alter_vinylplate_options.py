# Generated by Django 4.1.4 on 2023-01-05 17:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('musicDatabase', '0002_alter_vinylplate_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vinylplate',
            options={'ordering': ['related_release', 'plate_index']},
        ),
    ]
