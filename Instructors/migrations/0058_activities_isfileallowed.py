# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-09-06 04:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0057_auto_20170819_2135'),
    ]

    operations = [
        migrations.AddField(
            model_name='activities',
            name='isFileAllowed',
            field=models.BooleanField(default=True),
        ),
    ]
