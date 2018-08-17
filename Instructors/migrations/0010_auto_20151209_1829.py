# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0009_auto_20151123_1543'),
    ]

    operations = [
        migrations.AddField(
            model_name='activities',
            name='courseID',
            field=models.ForeignKey(to='Instructors.Courses', verbose_name='Course Name', default=2,on_delete=models.CASCADE),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='courseconfigparams',
            name='areBadgesDisplayed',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
