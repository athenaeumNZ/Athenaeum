# Generated by Django 4.1.4 on 2023-11-11 21:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0074_address_include_first_and_last_names'),
        ('accounts', '0086_remove_professionalservicesinvoice_client_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bankaccount',
            name='account_holder',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bank_account_account_holder', to='management.member'),
        ),
    ]
