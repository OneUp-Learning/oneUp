# Generated by Django 2.1.2 on 2019-05-10 19:59

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
        migrations.RemoveField(
            model_name='studentgoalsetting',
            name='progressToGoal',
        ),
    ]