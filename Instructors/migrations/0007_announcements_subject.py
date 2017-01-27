# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0006_milestones'),
    ]

    operations = [
        migrations.AddField(
            model_name='announcements',
            name='subject',
            field=models.CharField(default='   ', max_length=25),
            preserve_default=False,
        ),
    ]
