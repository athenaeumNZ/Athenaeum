# Generated by Django 4.1.4 on 2023-11-13 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('professionalServices', '0012_alter_professionalservicesinvoicehour_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='professionalservicesinvoicehour',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
    ]
