# Generated by Django 4.1.4 on 2023-03-26 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_cashbookentry_processing_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='cashbookentry',
            name='gst_should_be_included',
            field=models.BooleanField(default=True),
        ),
    ]