# Generated by Django 4.1.4 on 2023-03-24 01:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0063_member_account_credit'),
    ]

    operations = [
        migrations.AddField(
            model_name='vinyldistributor',
            name='weight_already_in_transit',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]