# Generated by Django 4.1.4 on 2023-01-13 03:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0008_rename_memberprofile_profile'),
    ]

    operations = [
        migrations.CreateModel(
            name='VinylColours',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(max_length=200)),
            ],
        ),
    ]