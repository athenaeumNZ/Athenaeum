# Generated by Django 4.1.4 on 2023-03-22 02:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0062_remove_member_bio_remove_member_birth_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='account_credit',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
