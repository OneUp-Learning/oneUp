# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0011_auto_20151218_0441'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenges',
            name='isVisable',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
