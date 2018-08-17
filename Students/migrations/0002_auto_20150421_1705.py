# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentchallenges',
            name='courseID',
            field=models.ForeignKey(default=1, to='Instructors.Courses', verbose_name='the related course',on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
