# Generated by Django 4.1.4 on 2023-06-19 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0029_orderrequestitem_stockpiled'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderrequestitem',
            name='invoiced',
            field=models.BooleanField(default=False),
        ),
    ]