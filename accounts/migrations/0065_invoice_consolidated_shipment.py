# Generated by Django 4.1.4 on 2023-06-29 00:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0064_shipment_arrived_at_consolidation_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='consolidated_shipment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='invoice_consolidated_shipment', to='accounts.shipment'),
        ),
    ]
