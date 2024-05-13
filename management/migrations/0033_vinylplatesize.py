# Generated by Django 4.1.4 on 2023-01-21 01:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0032_rename_cratevariations_cratevariation'),
    ]

    operations = [
        migrations.CreateModel(
            name='VinylPlateSize',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plate_size', models.CharField(max_length=200)),
            ],
            options={
                'ordering': ['plate_size'],
            },
        ),
    ]