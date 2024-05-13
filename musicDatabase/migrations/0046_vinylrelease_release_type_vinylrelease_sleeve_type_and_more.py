# Generated by Django 4.1.4 on 2023-02-19 23:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicDatabase', '0045_alter_vinylrelease_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='vinylrelease',
            name='release_type',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='vinylrelease',
            name='sleeve_type',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='vinylrelease',
            name='vinyl_color',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
