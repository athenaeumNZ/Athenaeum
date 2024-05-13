# Generated by Django 4.1.4 on 2023-04-10 18:15

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0020_alter_cashbookmonth_communications_forcast_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cashbookmonth',
            name='funds_introduced_forcast',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12),
        ),
        migrations.AlterField(
            model_name='cashbookmonth',
            name='gst_received_forcast',
            field=models.DecimalField(blank=True, decimal_places=2, default=Decimal('0'), max_digits=12),
        ),
        migrations.AlterField(
            model_name='cashbookmonth',
            name='interest_forcast',
            field=models.DecimalField(blank=True, decimal_places=2, default=Decimal('0'), max_digits=12),
        ),
        migrations.AlterField(
            model_name='cashbookmonth',
            name='sales_forcast',
            field=models.DecimalField(blank=True, decimal_places=2, default=Decimal('0'), max_digits=12),
        ),
    ]
