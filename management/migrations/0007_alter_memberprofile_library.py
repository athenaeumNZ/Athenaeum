# Generated by Django 4.1.4 on 2023-01-12 19:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0006_alter_memberprofile_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='memberprofile',
            name='library',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='management.library'),
        ),
    ]
