# Generated by Django 4.1.4 on 2023-12-29 01:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('musicDatabase', '0075_alter_vinylreleaserepressrequest_options'),
        ('management', '0083_vinylcondition_name'),
        ('accounts', '0102_remove_invoice_consolidated_shipment_and_more'),
        ('members', '0011_membermaybelist'),
    ]

    operations = [
        migrations.CreateModel(
            name='MemberPlate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='member_plate_member', to='management.member')),
            ],
        ),
        migrations.CreateModel(
            name='MemberRelease',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateField(auto_now_add=True)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='member_release_member', to='management.member')),
                ('order_request_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='member_release_order_request_item', to='accounts.orderrequestitem')),
            ],
        ),
        migrations.CreateModel(
            name='MemberReleaseStatusChoices',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name='memberunwantedlist',
            name='member',
        ),
        migrations.RemoveField(
            model_name='memberunwantedlist',
            name='unwanted_list',
        ),
        migrations.RemoveField(
            model_name='memberwantlist',
            name='member',
        ),
        migrations.RemoveField(
            model_name='memberwantlist',
            name='want_list',
        ),
        migrations.DeleteModel(
            name='MemberMaybeList',
        ),
        migrations.DeleteModel(
            name='MemberUnwantedList',
        ),
        migrations.DeleteModel(
            name='MemberWantlist',
        ),
        migrations.AddField(
            model_name='memberrelease',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='member_release_status', to='members.memberreleasestatuschoices'),
        ),
        migrations.AddField(
            model_name='memberrelease',
            name='vinyl_release',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='member_release_vinyl_release', to='musicDatabase.vinylrelease'),
        ),
        migrations.AddField(
            model_name='memberplate',
            name='member_release',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='member_plate_member_release', to='members.memberrelease'),
        ),
        migrations.AddField(
            model_name='memberplate',
            name='plate_condition',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='management.vinylcondition'),
        ),
        migrations.AddField(
            model_name='memberplate',
            name='vinyl_plate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='member_plate_vinyl_plate', to='musicDatabase.vinylplate'),
        ),
    ]