# Generated by Django 4.1.4 on 2023-03-19 05:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0004_orderitem_vinyl_release'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='on_order',
            field=models.BooleanField(default=False),
        ),
    ]
