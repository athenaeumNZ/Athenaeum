# Generated by Django 4.1.4 on 2023-02-17 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicDatabase', '0043_remove_aliases_artist_remove_artist_artist_is_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vinylplate',
            name='plate_index',
            field=models.CharField(default='a/b', max_length=20),
        ),
        migrations.AlterField(
            model_name='vinylrelease',
            name='country',
            field=models.CharField(default='UK', max_length=20),
        ),
        migrations.AlterField(
            model_name='vinylrelease',
            name='plate_count',
            field=models.CharField(default='1', max_length=20),
        ),
        migrations.AlterField(
            model_name='vinylrelease',
            name='track_count',
            field=models.CharField(default='2', max_length=20),
        ),
    ]
