# Generated by Django 2.0.8 on 2019-02-19 00:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0073_merge_20190208_1555'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='courseconfigparams',
            name='chatUsed',
        ),
    ]