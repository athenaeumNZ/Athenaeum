# Generated by Django 4.1.4 on 2023-12-26 01:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0081_alter_member_user'),
        ('vinylShop', '0032_alter_stockitem_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='shopgenre',
            unique_together={('library', 'genre')},
        ),
    ]
