# Generated by Django 4.1.4 on 2023-01-13 03:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0011_alter_vinylcolour_options'),
        ('vinylLibrary', '0010_alter_libraryplate_cover_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='libraryplate',
            name='vinyl_color',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='management.vinylcolour'),
        ),
    ]