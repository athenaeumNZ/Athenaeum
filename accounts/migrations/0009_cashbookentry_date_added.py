# Generated by Django 4.1.4 on 2023-03-26 23:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_cashbookinvoice'),
    ]

    operations = [
        migrations.AddField(
            model_name='cashbookentry',
            name='date_added',
            field=models.DateField(blank=True, null=True),
        ),
    ]
