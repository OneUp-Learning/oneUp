# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-26 01:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0035_uploadedimages_imagefilename'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assignedactivities',
            name='activityID',
        ),
        migrations.RemoveField(
            model_name='assignedactivities',
            name='recipientStudentID',
        ),
        migrations.DeleteModel(
            name='AssignedActivities',
        ),
    ]
