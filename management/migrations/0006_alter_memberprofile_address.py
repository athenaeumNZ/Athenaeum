# Generated by Django 4.1.4 on 2023-01-12 19:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0005_address_memberprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='memberprofile',
            name='address',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='management.address'),
        ),
    ]