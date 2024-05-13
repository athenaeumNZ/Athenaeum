# Generated by Django 4.1.4 on 2023-01-17 19:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicDatabase', '0026_alter_vinylrelease_release_date_confirmed'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArtistWrittenAs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('real_name', models.CharField(max_length=200)),
                ('use_this_artist_name', models.CharField(max_length=200)),
                ('aliases', models.TextField(max_length=1000)),
            ],
            options={
                'ordering': ['use_this_artist_name'],
            },
        ),
    ]
