# Generated by Django 4.1.4 on 2023-06-24 02:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0051_shipment_in_transit_alter_invoice_shipment'),
    ]

    operations = [
        migrations.AddField(
            model_name='courierpackage',
            name='en_route',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='courierpackage',
            name='invoiced',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='courierpackage',
            name='paid',
            field=models.BooleanField(default=False),
        ),
    ]