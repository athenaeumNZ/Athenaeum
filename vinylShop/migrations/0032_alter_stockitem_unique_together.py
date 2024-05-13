# Generated by Django 4.1.4 on 2023-12-24 03:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0081_alter_member_user'),
        ('musicDatabase', '0075_alter_vinylreleaserepressrequest_options'),
        ('vinylShop', '0031_stockitem_updated_by_librarian'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='stockitem',
            unique_together={('library', 'vinyl_release')},
        ),
    ]