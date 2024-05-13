# Generated by Django 4.1.4 on 2024-03-28 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicDatabase', '0081_vinylrelease_not_black'),
    ]

    operations = [
        migrations.AddField(
            model_name='vinylrelease',
            name='average_tracks_per_side',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]