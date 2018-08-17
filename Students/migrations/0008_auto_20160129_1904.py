# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0007_auto_20151218_0441'),
    ]

    operations = [
        migrations.RenameField(
            model_name='studentactivities',
            old_name='studentActivityID',
            new_name='studentActivityAssignmentID',
        ),
        migrations.AlterField(
            model_name='studentactivities',
            name='activityID',
            field=models.ForeignKey(verbose_name='the related activity', to='Instructors.Activities',on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
