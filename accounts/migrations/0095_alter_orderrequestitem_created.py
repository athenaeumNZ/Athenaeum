# Generated by Django 4.1.4 on 2023-12-17 02:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0094_orderrequestitem_created_orderrequestitem_library_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderrequestitem',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
