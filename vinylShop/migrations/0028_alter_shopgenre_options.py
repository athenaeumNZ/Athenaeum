# Generated by Django 4.1.4 on 2023-12-19 03:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vinylShop', '0027_remove_shopgenre_member_shopgenre_library'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shopgenre',
            options={'ordering': ['genre']},
        ),
    ]
