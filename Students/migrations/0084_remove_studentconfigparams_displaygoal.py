# Generated by Django 2.1.2 on 2019-05-07 01:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0083_merge_20190423_1332'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentconfigparams',
            name='displayGoal',
        ),
    ]
