# Generated by Django 4.1.4 on 2023-12-28 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0082_remove_library_librarian_library_library_shop'),
    ]

    operations = [
        migrations.AddField(
            model_name='vinylcondition',
            name='name',
            field=models.CharField(default='', max_length=200),
        ),
    ]