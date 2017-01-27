# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0010_studentregisteredcourses'),
        ('Instructors', '0013_instructorregisteredcourses'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignedActivities',
            fields=[
                ('activityAssigmentID', models.AutoField(serialize=False, primary_key=True)),
                ('pointsReceived', models.IntegerField()),
                ('activityID', models.ForeignKey(to='Instructors.Activities', verbose_name='Activity ID')),
                ('recipientStudentID', models.ForeignKey(to='Students.Student', verbose_name='Recipient Student ID')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
