# Generated by Django 4.1.4 on 2023-08-14 04:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0066_orderrequest_archived'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shipment',
            old_name='received',
            new_name='arrived',
        ),
    ]
