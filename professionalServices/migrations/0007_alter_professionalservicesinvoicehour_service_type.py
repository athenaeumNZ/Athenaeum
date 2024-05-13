# Generated by Django 4.1.4 on 2023-11-10 23:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('professionalServices', '0006_professionalservicesinvoicehour_service_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='professionalservicesinvoicehour',
            name='service_type',
            field=models.ForeignKey(blank=True, limit_choices_to={'service_provider': 'invoice__service_provider'}, null=True, on_delete=django.db.models.deletion.CASCADE, to='professionalServices.professionalserviceproviderservice'),
        ),
    ]
