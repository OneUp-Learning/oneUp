# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-27 22:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0019_auto_20160427_0517'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='challenges',
            name='feedbackOption',
        ),
        migrations.AddField(
            model_name='challenges',
            name='feedbackOption1',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='challenges',
            name='feedbackOption2',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='challenges',
            name='feedbackOption3',
            field=models.BooleanField(default=False),
        ),
    ]
