# Generated by Django 4.1.4 on 2023-02-02 00:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0042_remove_vinyldistributor_shipping_cost_to_nz'),
        ('musicDatabase', '0040_vinylrelease_sale_price_nz_and_more'),
        ('vinylLibrary', '0047_alter_librarysalevinyl_related_release'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='librarysalevinyl',
            unique_together={('related_release', 'library')},
        ),
    ]
