# Generated by Django 4.1.4 on 2023-04-10 18:13

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0019_alter_cashbookmonth_bank_fee_forcast'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cashbookmonth',
            name='communications_forcast',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12),
        ),
        migrations.AlterField(
            model_name='cashbookmonth',
            name='consumables_forcast',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12),
        ),
        migrations.AlterField(
            model_name='cashbookmonth',
            name='drawings_forcast',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12),
        ),
        migrations.AlterField(
            model_name='cashbookmonth',
            name='fit_out_forcast',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12),
        ),
        migrations.AlterField(
            model_name='cashbookmonth',
            name='home_forcast',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12),
        ),
        migrations.AlterField(
            model_name='cashbookmonth',
            name='professional_forcast',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12),
        ),
        migrations.AlterField(
            model_name='cashbookmonth',
            name='shipping_forcast',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12),
        ),
        migrations.AlterField(
            model_name='cashbookmonth',
            name='stock_forcast',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12),
        ),
        migrations.AlterField(
            model_name='cashbookmonth',
            name='sundry_forcast',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12),
        ),
    ]