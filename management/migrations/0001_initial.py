# Generated by Django 4.1.4 on 2023-01-05 15:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import multiselectfield.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Crate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('crate_id', models.CharField(max_length=20)),
                ('crate_description', models.CharField(default='', max_length=150)),
                ('crate_energy_level', models.IntegerField(choices=[(0, '-'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6')], default=1)),
                ('crate_genre', models.CharField(choices=[('-', '-'), ('DNB', 'DNB'), ('Jungle 94-00', 'Jungle 94-00'), ('Jungle 10-', 'Jungle 10-'), ('Dubstep', 'Dubstep'), ('Grime', 'Grime'), ('Liquid DNB', 'Liquid DNB'), ('NeuroFunk 04-', 'NeuroFunk 04-'), ('NeuroFunk 98-03', 'NeuroFunk 98-03'), ('Minimal DNB', 'Minimal DNB'), ('Halftime', 'Halftime')], default='DNB', max_length=50)),
                ('crate_mix', models.FileField(blank=True, upload_to='static/management/crateMixes')),
                ('crate_vibe', models.CharField(choices=[('-', '-'), ('Yellow', 'Yellow'), ('Blue', 'Blue'), ('Red', 'Red'), ('Green', 'Green')], default='Red', max_length=20)),
            ],
            options={
                'ordering': ['crate_id'],
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('country', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('website', models.CharField(max_length=500)),
                ('supplier_of', multiselectfield.db.fields.MultiSelectField(choices=[('Cables', 'Cables'), ('Cases', 'Cases'), ('CDJs', 'CDJs'), ('Cleaning', 'Cleaning'), ('Controllers', 'Controllers'), ('Dividers', 'Dividers'), ('Headphones', 'Headphones'), ('Mixer', 'Mixer'), ('Monitors', 'Monitors'), ('Needles', 'Needles'), ('Sleeve', 'Sleeve'), ('Turntable', 'Turntable')], max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ShopItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=2000)),
                ('image', models.FileField(blank=True, null=True, upload_to='static/management/shop/shop_item_images')),
                ('product_info_link', models.CharField(blank=True, max_length=500)),
                ('type', models.CharField(blank=True, choices=[('Cables', 'Cables'), ('Cases', 'Cases'), ('CDJs', 'CDJs'), ('Cleaning', 'Cleaning'), ('Controllers', 'Controllers'), ('Dividers', 'Dividers'), ('Headphones', 'Headphones'), ('Mixer', 'Mixer'), ('Monitors', 'Monitors'), ('Needles', 'Needles'), ('Sleeve', 'Sleeve'), ('Turntable', 'Turntable')], max_length=20)),
                ('recommended_supplier', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='management.supplier')),
            ],
        ),
        migrations.CreateModel(
            name='Library',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('unit_number', models.CharField(blank=True, max_length=10)),
                ('street_number', models.CharField(blank=True, max_length=10)),
                ('street_name', models.CharField(blank=True, max_length=100)),
                ('suburb', models.CharField(blank=True, max_length=100)),
                ('city', models.CharField(blank=True, max_length=100)),
                ('post_code', models.CharField(blank=True, max_length=100)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('description', models.CharField(blank=True, max_length=2000)),
                ('date_established', models.DateField(auto_now_add=True)),
                ('logo_black_on_white', models.FileField(blank=True, upload_to='static/vinyllibrary/librarylogos')),
                ('logo_white_on_black', models.FileField(blank=True, upload_to='static/vinyllibrary/librarylogos')),
                ('cue_points', models.CharField(choices=[('No', 'No'), ('Yes', 'Yes')], default='Yes', max_length=20, verbose_name='All plates have Maxwell cue points?')),
                ('sleeve_catalog', models.CharField(choices=[('No', 'No'), ('Yes', 'Yes')], default='Yes', max_length=20, verbose_name='All outersleeves have catalog number sticker on top?')),
                ('info_sheet', models.CharField(choices=[('No', 'No'), ('Yes', 'Yes')], default='Yes', max_length=20, verbose_name='All plates come with Maxwell cover sheet?')),
                ('plate_stickers', models.CharField(choices=[('No', 'No'), ('Yes', 'Yes')], default='Yes', max_length=20, verbose_name='All plates have non cue point stickers removed?')),
                ('outersleeve_stickers', models.CharField(choices=[('No', 'No'), ('Yes', 'Yes')], default='Yes', max_length=20, verbose_name='All outersleeves have stickers removed?')),
                ('finger_nails', models.CharField(choices=[('No', 'No'), ('Yes', 'Yes')], default='Yes', max_length=20, verbose_name='Members finger nails must be trimmed and filed?')),
                ('records_playable', models.CharField(choices=[('No', 'No'), ('Yes', 'Yes')], default='Yes', max_length=20, verbose_name='Records can be played?')),
                ('records_mixable', models.CharField(choices=[('No', 'No'), ('Yes', 'Yes')], default='Yes', max_length=20, verbose_name='Records can be mixed?')),
                ('non_members', models.CharField(choices=[('No', 'No'), ('Yes', 'Yes')], default='Yes', max_length=20, verbose_name='Only members can play or handle or mix records?')),
                ('outdoor_playing', models.CharField(choices=[('No', 'No'), ('Yes', 'Yes')], default='No', max_length=20, verbose_name='Records can be played outdoors?')),
                ('library_cleanroom', models.CharField(choices=[('No', 'No'), ('Yes', 'Yes')], default='No', max_length=20, verbose_name='Environment is a classified cleanroom?')),
                ('library_controled_temperature', models.CharField(choices=[('No', 'No'), ('Yes', 'Yes')], default='Yes', max_length=20, verbose_name='Library has 24/7 365 temperature control?')),
                ('library_dry_wipe_tops_of_crates', models.CharField(choices=[('Before Use', 'Before Use'), ('After Use', 'After Use'), ('Daily', 'Daily'), ('Twice a week', 'Twice a week'), ('Once a week', 'Once a week'), ('Fortnightly', 'Fortnightly'), ('Monthly', 'Monthly'), ('Never', 'Never')], default='Before Use', max_length=100)),
                ('library_dry_wiped', models.CharField(choices=[('Before Use', 'Before Use'), ('After Use', 'After Use'), ('Daily', 'Daily'), ('Twice a week', 'Twice a week'), ('Once a week', 'Once a week'), ('Fortnightly', 'Fortnightly'), ('Monthly', 'Monthly'), ('Never', 'Never')], default='Once a week', max_length=100)),
                ('library_smoking', models.CharField(choices=[('No', 'No'), ('Yes', 'Yes')], default='No', max_length=20, verbose_name='Smoking is allowed in the library?')),
                ('library_gloves', models.CharField(choices=[('No', 'No'), ('Yes', 'Yes')], default='No', max_length=20, verbose_name='Cotton Gloves are required when handeling records?')),
                ('library_thoroughfare', models.CharField(choices=[('No', 'No'), ('Yes', 'Yes')], default='No', max_length=20, verbose_name='Library is located in a thoroughfare?')),
                ('library_turntables_dusted_and_vacummed', models.CharField(choices=[('Before Use', 'Before Use'), ('After Use', 'After Use'), ('Daily', 'Daily'), ('Twice a week', 'Twice a week'), ('Once a week', 'Once a week'), ('Fortnightly', 'Fortnightly'), ('Monthly', 'Monthly'), ('Never', 'Never')], default='Before Use', max_length=100)),
                ('library_vacuumed', models.CharField(choices=[('Before Use', 'Before Use'), ('After Use', 'After Use'), ('Daily', 'Daily'), ('Twice a week', 'Twice a week'), ('Once a week', 'Once a week'), ('Fortnightly', 'Fortnightly'), ('Monthly', 'Monthly'), ('Never', 'Never')], default='Once a week', max_length=100)),
                ('library_vestibule', models.CharField(choices=[('No', 'No'), ('Yes', 'Yes')], default='No', max_length=20, verbose_name='Library has a dust control vestibule?')),
                ('library_wet_wiped', models.CharField(choices=[('Before Use', 'Before Use'), ('After Use', 'After Use'), ('Daily', 'Daily'), ('Twice a week', 'Twice a week'), ('Once a week', 'Once a week'), ('Fortnightly', 'Fortnightly'), ('Monthly', 'Monthly'), ('Never', 'Never')], default='Fortnightly', max_length=100)),
                ('studio_cleanroom', models.CharField(choices=[('No', 'No'), ('Yes', 'Yes')], default='No', max_length=20, verbose_name='Studio is a classified cleanroom?')),
                ('studio_controled_temperature', models.CharField(choices=[('No', 'No'), ('Yes', 'Yes')], default='Yes', max_length=20, verbose_name='Studio has 24/7 365 temperature control?')),
                ('studio_dry_wipe_tops_of_crates', models.CharField(choices=[('Before Use', 'Before Use'), ('After Use', 'After Use'), ('Daily', 'Daily'), ('Twice a week', 'Twice a week'), ('Once a week', 'Once a week'), ('Fortnightly', 'Fortnightly'), ('Monthly', 'Monthly'), ('Never', 'Never')], default='Before Use', max_length=100)),
                ('studio_dry_wiped', models.CharField(choices=[('Before Use', 'Before Use'), ('After Use', 'After Use'), ('Daily', 'Daily'), ('Twice a week', 'Twice a week'), ('Once a week', 'Once a week'), ('Fortnightly', 'Fortnightly'), ('Monthly', 'Monthly'), ('Never', 'Never')], default='Once a week', max_length=100)),
                ('studio_smoking', models.CharField(choices=[('No', 'No'), ('Yes', 'Yes')], default='No', max_length=20, verbose_name='Smoking is allowed in the studio?')),
                ('studio_gloves', models.CharField(choices=[('No', 'No'), ('Yes', 'Yes')], default='No', max_length=20, verbose_name='Cotton Gloves are required when handeling records?')),
                ('studio_thoroughfare', models.CharField(choices=[('No', 'No'), ('Yes', 'Yes')], default='No', max_length=20, verbose_name='Studio is located in a thoroughfare?')),
                ('studio_turntables_dusted_and_vacummed', models.CharField(choices=[('Before Use', 'Before Use'), ('After Use', 'After Use'), ('Daily', 'Daily'), ('Twice a week', 'Twice a week'), ('Once a week', 'Once a week'), ('Fortnightly', 'Fortnightly'), ('Monthly', 'Monthly'), ('Never', 'Never')], default='Before Use', max_length=100)),
                ('studio_vacuumed', models.CharField(choices=[('Before Use', 'Before Use'), ('After Use', 'After Use'), ('Daily', 'Daily'), ('Twice a week', 'Twice a week'), ('Once a week', 'Once a week'), ('Fortnightly', 'Fortnightly'), ('Monthly', 'Monthly'), ('Never', 'Never')], default='Once a week', max_length=100)),
                ('studio_vestibule', models.CharField(choices=[('No', 'No'), ('Yes', 'Yes')], default='No', max_length=20, verbose_name='Studio has a dust control vestibule?')),
                ('studio_wet_wiped', models.CharField(choices=[('Before Use', 'Before Use'), ('After Use', 'After Use'), ('Daily', 'Daily'), ('Twice a week', 'Twice a week'), ('Once a week', 'Once a week'), ('Fortnightly', 'Fortnightly'), ('Monthly', 'Monthly'), ('Never', 'Never')], default='Fortnightly', max_length=100)),
                ('libarian', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='librarians', to=settings.AUTH_USER_MODEL)),
                ('members', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
