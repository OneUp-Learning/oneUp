# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-26 01:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0020_auto_20170221_1321'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentactivities',
            name='courseID',
        ),
        migrations.AlterField(
            model_name='studentactivities',
            name='instructorFeedback',
            field=models.CharField(default='  ', max_length=200),
        ),
    ]
