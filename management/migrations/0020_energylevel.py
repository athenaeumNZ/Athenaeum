# Generated by Django 4.1.4 on 2023-01-16 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0019_vibe'),
    ]

    operations = [
        migrations.CreateModel(
            name='EnergyLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('energy_level', models.CharField(max_length=200)),
            ],
            options={
                'ordering': ['energy_level'],
            },
        ),
    ]
