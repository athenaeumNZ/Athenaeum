# Generated by Django 4.1.4 on 2023-12-19 03:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0081_alter_member_user'),
        ('vinylShop', '0026_shopgenre'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shopgenre',
            name='member',
        ),
        migrations.AddField(
            model_name='shopgenre',
            name='library',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='management.library'),
            preserve_default=False,
        ),
    ]