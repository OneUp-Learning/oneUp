# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-10-02 15:34
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0041_merge_20170919_1804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentactivities',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
