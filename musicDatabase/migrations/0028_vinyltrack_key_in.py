# Generated by Django 4.1.4 on 2023-01-21 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicDatabase', '0027_artistwrittenas'),
    ]

    operations = [
        migrations.AddField(
            model_name='vinyltrack',
            name='key_in',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]
