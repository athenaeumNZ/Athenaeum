# Generated by Django 4.1.4 on 2023-12-19 01:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('musicDatabase', '0070_rename_not_all_catergorized_vinylrelease_not_all_categorized'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vinylrelease',
            old_name='supplier',
            new_name='distributor',
        ),
    ]