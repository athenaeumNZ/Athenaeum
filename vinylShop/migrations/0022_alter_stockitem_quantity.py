# Generated by Django 4.1.4 on 2023-12-17 03:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vinylShop', '0021_alter_stockitem_quantity_incoming'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockitem',
            name='quantity',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
