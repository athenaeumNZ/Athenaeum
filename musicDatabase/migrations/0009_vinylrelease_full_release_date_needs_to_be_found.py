# Generated by Django 4.1.4 on 2023-01-07 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicDatabase', '0008_remove_vinylrelease_release_month_year_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='vinylrelease',
            name='full_release_date_needs_to_be_found',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]