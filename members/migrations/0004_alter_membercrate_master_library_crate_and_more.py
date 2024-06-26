# Generated by Django 4.1.4 on 2023-02-08 10:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0043_alter_crate_genre'),
        ('vinylLibrary', '0051_alter_librarysalevinyl_unique_together_and_more'),
        ('members', '0003_membercrate_related_crate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membercrate',
            name='master_library_crate',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='member_crates', to='vinylLibrary.librarycrate'),
        ),
        migrations.AlterField(
            model_name='membercrate',
            name='member',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='member_crates', to='management.member'),
        ),
        migrations.AlterField(
            model_name='membercrate',
            name='related_crate',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='member_crates', to='management.crate'),
        ),
    ]
