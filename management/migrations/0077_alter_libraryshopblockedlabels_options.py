# Generated by Django 4.1.4 on 2023-11-24 21:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0076_libraryshopblockedlabels'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='libraryshopblockedlabels',
            options={'ordering': ['label_name']},
        ),
    ]