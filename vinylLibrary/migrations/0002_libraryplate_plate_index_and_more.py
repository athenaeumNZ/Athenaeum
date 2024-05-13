# Generated by Django 4.1.4 on 2023-01-05 15:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('musicDatabase', '0001_initial'),
        ('vinylLibrary', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='libraryplate',
            name='plate_index',
            field=models.CharField(choices=[('a/b', 'a/b'), ('c/d', 'c/d'), ('e/f', 'e/f'), ('g/h', 'g/h'), ('i/j', 'i/j'), ('k/l', 'k/l'), ('m/n', 'm/n'), ('o/p', 'o/p'), ('q/r', 'q/r'), ('s/t', 's/t'), ('u/v', 'u/v'), ('w/x', 'w/x'), ('y/z', 'y/z'), ('x/y', 'x,y'), ('xx/yy', 'xx/yy'), ('a/c', 'a/c')], default='a/b', max_length=20),
        ),
        migrations.AddField(
            model_name='libraryplate',
            name='related_vinyl_release',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='musicDatabase.vinylrelease'),
        ),
    ]
