# Generated by Django 4.1.4 on 2023-02-28 00:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0054_alter_member_birth_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='address',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='management.address'),
        ),
    ]
