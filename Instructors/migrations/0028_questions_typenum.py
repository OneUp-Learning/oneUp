# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-12-21 18:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0027_auto_20161104_1753'),
    ]

    operations = [
        migrations.AddField(
            model_name='questions',
            name='typeNum',
            field=models.IntegerField(default=0),
        ),
    ]
