# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0005_studentactivities'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentactivities',
            name='activityID',
            field=models.ForeignKey(to='Instructors.Activities', verbose_name='the related student'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentactivities',
            name='courseID',
            field=models.ForeignKey(default=1, verbose_name='the related course', to='Instructors.Courses'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='studentactivities',
            name='studentID',
            field=models.ForeignKey(to='Students.Student', verbose_name='the related student'),
            preserve_default=True,
        ),
    ]
