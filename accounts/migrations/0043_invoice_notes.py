# Generated by Django 4.1.4 on 2023-06-21 01:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0042_alter_invoice_shipment'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='notes',
            field=models.TextField(max_length=1000, null=True),
        ),
    ]
