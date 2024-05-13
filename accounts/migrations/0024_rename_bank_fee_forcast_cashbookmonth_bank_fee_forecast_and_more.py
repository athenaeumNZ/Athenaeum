# Generated by Django 4.1.4 on 2023-04-10 21:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0023_remove_cashbookmonth_gst_received_forcast_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cashbookmonth',
            old_name='bank_fee_forcast',
            new_name='bank_fee_forecast',
        ),
        migrations.RenameField(
            model_name='cashbookmonth',
            old_name='communications_forcast',
            new_name='communications_forecast',
        ),
        migrations.RenameField(
            model_name='cashbookmonth',
            old_name='consumables_forcast',
            new_name='consumables_forecast',
        ),
        migrations.RenameField(
            model_name='cashbookmonth',
            old_name='drawings_forcast',
            new_name='drawings_forecast',
        ),
        migrations.RenameField(
            model_name='cashbookmonth',
            old_name='fit_out_forcast',
            new_name='fit_out_forecast',
        ),
        migrations.RenameField(
            model_name='cashbookmonth',
            old_name='funds_introduced_forcast',
            new_name='funds_introduced_forecast',
        ),
        migrations.RenameField(
            model_name='cashbookmonth',
            old_name='home_forcast',
            new_name='home_forecast',
        ),
        migrations.RenameField(
            model_name='cashbookmonth',
            old_name='interest_forcast',
            new_name='interest_forecast',
        ),
        migrations.RenameField(
            model_name='cashbookmonth',
            old_name='opening_balance_forcast',
            new_name='opening_balance_forecast',
        ),
        migrations.RenameField(
            model_name='cashbookmonth',
            old_name='professional_forcast',
            new_name='professional_forecast',
        ),
        migrations.RenameField(
            model_name='cashbookmonth',
            old_name='sales_forcast',
            new_name='sales_forecast',
        ),
        migrations.RenameField(
            model_name='cashbookmonth',
            old_name='shipping_forcast',
            new_name='shipping_forecast',
        ),
        migrations.RenameField(
            model_name='cashbookmonth',
            old_name='stock_forcast',
            new_name='stock_forecast',
        ),
        migrations.RenameField(
            model_name='cashbookmonth',
            old_name='sundry_forcast',
            new_name='sundry_forecast',
        ),
    ]
