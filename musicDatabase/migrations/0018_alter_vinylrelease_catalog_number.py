# Generated by Django 4.1.4 on 2023-01-12 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicDatabase', '0017_alter_vinylplate_related_release_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vinylrelease',
            name='catalog_number',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
