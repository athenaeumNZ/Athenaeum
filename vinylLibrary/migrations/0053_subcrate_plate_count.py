# Generated by Django 4.1.4 on 2023-02-09 22:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vinylLibrary', '0052_libraryplate_related_member_crate'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcrate',
            name='plate_count',
            field=models.CharField(default='0', max_length=20),
        ),
    ]
