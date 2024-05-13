# Generated by Django 4.1.4 on 2023-12-19 02:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0081_alter_member_user'),
        ('vinylShop', '0025_stockitem_unavailable'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShopGenre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genre', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='management.genre')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='management.member')),
            ],
        ),
    ]