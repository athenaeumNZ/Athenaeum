# Generated by Django 4.1.4 on 2023-08-21 22:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0067_rename_received_shipment_arrived'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoiceitem',
            name='flattened_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
