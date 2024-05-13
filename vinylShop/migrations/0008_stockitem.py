# Generated by Django 4.1.4 on 2023-06-24 06:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('musicDatabase', '0067_vinylrelease_most_common'),
        ('management', '0068_address_island'),
        ('vinylShop', '0007_remove_cashbookentry_bank_account_used_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('quantity', models.PositiveIntegerField(blank=True, null=True)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='management.member')),
                ('release', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='musicDatabase.vinylrelease')),
            ],
        ),
    ]
