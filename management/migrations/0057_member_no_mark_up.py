# Generated by Django 4.1.4 on 2023-03-01 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0056_address_c_o'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='no_mark_up',
            field=models.BooleanField(default=False),
        ),
    ]