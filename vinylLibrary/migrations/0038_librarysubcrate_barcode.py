# Generated by Django 4.1.4 on 2023-01-21 21:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vinylLibrary', '0037_libraryplate_barcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='librarysubcrate',
            name='barcode',
            field=models.ImageField(blank=True, upload_to='static/vinylLibrary/librarySubCrateBarcodes'),
        ),
    ]
