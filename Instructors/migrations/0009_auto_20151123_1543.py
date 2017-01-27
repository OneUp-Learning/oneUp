# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0008_courseconfigparams'),
    ]

    operations = [
        migrations.AlterField(
            model_name='announcements',
            name='subject',
            field=models.CharField(max_length=25, default='  '),
            preserve_default=True,
        ),
    ]
