# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0025_auto_20161026_1854'),
    ]

    operations = [
        migrations.AlterField(
            model_name='challenges',
            name='endTimestamp',
            field=models.DateTimeField(default=datetime.datetime.now, blank=True),
        ),
        migrations.AlterField(
            model_name='challenges',
            name='startTimestamp',
            field=models.DateTimeField(default=datetime.datetime.now, blank=True),
        ),
    ]
