# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-05-09 20:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0083_activities_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='announcements',
            name='message',
            field=models.CharField(default='', max_length=1000),
        ),
    ]
