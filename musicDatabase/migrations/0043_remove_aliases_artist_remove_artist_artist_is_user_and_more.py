# Generated by Django 4.1.4 on 2023-02-17 20:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('musicDatabase', '0042_vinylrelease_supplier_item_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aliases',
            name='artist',
        ),
        migrations.RemoveField(
            model_name='artist',
            name='artist_is_user',
        ),
        migrations.DeleteModel(
            name='Label',
        ),
        migrations.DeleteModel(
            name='Aliases',
        ),
        migrations.DeleteModel(
            name='Artist',
        ),
    ]