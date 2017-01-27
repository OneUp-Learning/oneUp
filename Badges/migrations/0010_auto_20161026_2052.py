# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0009_auto_20161026_1854'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='leaderboards',
            name='courseID',
        ),
        migrations.RemoveField(
            model_name='leaderboards',
            name='studentID',
        ),
        migrations.RemoveField(
            model_name='studentconfigparams',
            name='ccpID',
        ),
        migrations.RemoveField(
            model_name='studentconfigparams',
            name='courseID',
        ),
        migrations.RemoveField(
            model_name='studentconfigparams',
            name='studentID',
        ),
        migrations.DeleteModel(
            name='Leaderboards',
        ),
        migrations.DeleteModel(
            name='StudentConfigParams',
        ),
    ]
