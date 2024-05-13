# Generated by Django 4.1.4 on 2023-01-30 19:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0039_vinyldistributor'),
        ('musicDatabase', '0037_vinylrelease_cost_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vinylrelease',
            name='supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='management.vinyldistributor'),
        ),
    ]
