# Generated by Django 4.1.4 on 2023-04-29 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musicDatabase', '0065_alter_vinylrelease_finalized'),
    ]

    operations = [
        migrations.AddField(
            model_name='vinylrelease',
            name='artwork_small',
            field=models.ImageField(blank=True, null=True, upload_to='static/musicDatabase/releaseArtworkSmall'),
        ),
    ]
