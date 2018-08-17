# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0003_challengestopics'),
        ('Students', '0004_studentbadges'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentActivities',
            fields=[
                ('studentActivityID', models.AutoField(serialize=False, primary_key=True)),
                ('timestamp', models.DateTimeField()),
                ('activityScore', models.DecimalField(max_digits=6, decimal_places=2)),
                ('instructorFeedback', models.CharField(max_length=200)),
                ('activityID', models.ForeignKey(verbose_name=b'the related student', to='Instructors.Activities',on_delete=models.CASCADE)),
                ('courseID', models.ForeignKey(default=1, verbose_name=b'the related course', to='Instructors.Courses',on_delete=models.CASCADE)),
                ('studentID', models.ForeignKey(verbose_name=b'the related student', to='Students.Student',on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
