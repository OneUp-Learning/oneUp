# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-22 01:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0022_auto_20160916_2205'),
    ]

    operations = [
        migrations.RenameField(
            model_name='courseconfigparams',
            old_name='isCourseBucksDisplayed',
            new_name='isVirtualCurrencyDisplayed',
        ),
        migrations.RemoveField(
            model_name='courseconfigparams',
            name='courseAuthor',
        ),
        migrations.AddField(
            model_name='courseconfigparams',
            name='isAvatarDisplayed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='courseconfigparams',
            name='isLeaderBoardDisplayed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='courseconfigparams',
            name='isLevellingDisplayed',
            field=models.BooleanField(default=False),
        ),
    ]
