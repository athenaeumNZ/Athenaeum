# Generated by Django 4.1.4 on 2023-01-16 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0023_country_alter_crate_crate_energy_level_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Count',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=200)),
            ],
            options={
                'ordering': ['number'],
            },
        ),
    ]