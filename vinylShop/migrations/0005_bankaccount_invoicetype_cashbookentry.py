# Generated by Django 4.1.4 on 2023-03-23 00:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0063_member_account_credit'),
        ('vinylShop', '0004_weeklyreleasesheet_release_sheet_finalized'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_name', models.DateField(blank=True, null=True)),
                ('account_number', models.IntegerField()),
                ('opening_balance', models.DecimalField(decimal_places=2, max_digits=10)),
                ('account_holder', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='management.member')),
            ],
        ),
        migrations.CreateModel(
            name='InvoiceType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='CashBookEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_date', models.DateField(blank=True, null=True)),
                ('invoice_reference', models.CharField(max_length=100)),
                ('amount_NZD', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_expense', models.BooleanField(default=False)),
                ('uploaded_invoice', models.FileField(blank=True, upload_to='static/vinylShop/cashFlowUploadedInvoices')),
                ('reconciled', models.BooleanField(default=False)),
                ('bank_account_used', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='vinylShop.bankaccount')),
                ('invoice_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='vinylShop.invoicetype')),
            ],
            options={
                'ordering': ['-reconciled', '-invoice_date'],
            },
        ),
    ]
