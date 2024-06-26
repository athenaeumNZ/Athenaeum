# Generated by Django 4.1.4 on 2023-01-19 19:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('musicDatabase', '0027_artistwrittenas'),
        ('vinylLibrary', '0031_alter_librarycrate_library_crate_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='WantlistPlate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('related_vinyl_plate', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='musicDatabase.vinylplate')),
            ],
            options={
                'ordering': ['related_vinyl_plate'],
            },
        ),
    ]
