# Generated by Django 4.1.4 on 2023-12-17 00:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vinylShop', '0018_stockitem_auto_restock_stockitem_auto_restock_level'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stockitem',
            old_name='auto_restock_level',
            new_name='auto_restock_threshold',
        ),
        migrations.AddField(
            model_name='stockitem',
            name='auto_restock_quantity',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
