# Generated by Django 4.1.4 on 2023-08-25 04:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicDatabase', '0068_remove_vinylrelease_finalized_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='vinylrelease',
            name='back_in_stock',
            field=models.BooleanField(default=False),
        ),
    ]
