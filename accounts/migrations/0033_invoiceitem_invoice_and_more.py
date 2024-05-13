# Generated by Django 4.1.4 on 2023-06-20 01:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0032_alter_invoiceitem_order_request_item'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoiceitem',
            name='invoice',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='invoice_items__invoice+', to='accounts.invoice'),
        ),
        migrations.AlterField(
            model_name='invoiceitem',
            name='order_request_item',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='order_request_items__invoice+', to='accounts.orderrequestitem'),
        ),
    ]
