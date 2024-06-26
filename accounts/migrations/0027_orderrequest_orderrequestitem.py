# Generated by Django 4.1.4 on 2023-06-18 22:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('musicDatabase', '0067_vinylrelease_most_common'),
        ('management', '0067_member_active'),
        ('accounts', '0026_cashbookmonth_logistics_forecast'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('library', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='management.library')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='management.member')),
            ],
            options={
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='OrderRequestItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordered', models.BooleanField(default=False)),
                ('sent_to_invoice_receipt', models.BooleanField(default=False)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('order_request', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='order_request_items__order_request+', to='accounts.orderrequest')),
                ('vinyl_release', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='order_request_items__vinyl_release+', to='musicDatabase.vinylrelease')),
            ],
        ),
    ]
