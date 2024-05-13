# Generated by Django 4.1.4 on 2023-01-05 20:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vinylLibrary', '0004_libraryplate_cover'),
    ]

    operations = [
        migrations.AlterField(
            model_name='libraryplate',
            name='cover',
            field=models.CharField(blank=True, choices=[('Inner Sleeve', 'Inner Sleeve'), ('Full Artwork', 'Full Artwork'), ('Top Sticker Artwork', 'Top Sticker Artwork'), ('Record Label Sleeve', 'Record Label Sleeve'), ('Generic', 'Generic')], default='Inner Sleeve', max_length=100),
        ),
        migrations.AlterField(
            model_name='libraryplate',
            name='related_library_crate',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='related_library_plate', to='vinylLibrary.librarycrate'),
        ),
    ]
