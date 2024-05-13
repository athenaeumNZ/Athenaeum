# Generated by Django 4.1.4 on 2023-02-09 11:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vinylLibrary', '0051_alter_librarysalevinyl_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='libraryplate',
            name='related_member_crate',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='related_library_plate', to='vinylLibrary.subcrate'),
        ),
    ]
