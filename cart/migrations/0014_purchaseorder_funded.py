# Generated by Django 4.1.4 on 2023-03-31 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0013_purchaseorderitem_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorder',
            name='funded',
            field=models.BooleanField(default=False),
        ),
    ]