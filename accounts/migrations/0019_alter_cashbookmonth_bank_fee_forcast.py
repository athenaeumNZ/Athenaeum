# Generated by Django 4.1.4 on 2023-04-10 17:57

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0018_cashbookmonth_gst_received_forcast'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cashbookmonth',
            name='bank_fee_forcast',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12),
        ),
    ]