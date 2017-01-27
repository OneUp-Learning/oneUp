# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0010_studentregisteredcourses'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentbadges',
            name='objectID',
            field=models.IntegerField(default=-1, verbose_name='index into the appropriate table'),
            preserve_default=True,
        ),
    ]
