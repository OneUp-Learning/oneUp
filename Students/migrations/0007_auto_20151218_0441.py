# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-18 04:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0006_auto_20151029_1723'),
    ]

    operations = [
        migrations.AddField(
            model_name='studenteventlog',
            name='objectID',
            field=models.IntegerField(default=-1, verbose_name='index into the appropriate table'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='studenteventlog',
            name='objectType',
            field=models.IntegerField(default=0, verbose_name='which type of object is involved, for example, challenge, individual question, or other activity.  Should be a reference to an objectType Enum'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='studentcourseskills',
            name='skillPoints',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='studenteventlog',
            name='event',
            field=models.IntegerField(db_index=True, default=-1, verbose_name='the event which occurred.  Should be a reference to the Event enum'),
        ),
    ]
