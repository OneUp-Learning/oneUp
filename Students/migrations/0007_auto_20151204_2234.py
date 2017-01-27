# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0006_auto_20151029_1723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentactivities',
            name='activityID',
            field=models.ForeignKey(verbose_name='the related activity', to='Instructors.Activities'),
            preserve_default=True,
        ),
    ]
