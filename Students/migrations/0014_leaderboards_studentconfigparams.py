# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0026_auto_20161026_2052'),
        ('Students', '0013_merge_20161021_1451'),
    ]

    operations = [
        migrations.CreateModel(
            name='Leaderboards',
            fields=[
                ('leaderboardID', models.AutoField(primary_key=True, serialize=False)),
                ('courseID', models.ForeignKey(to='Instructors.Courses', verbose_name='Course Name',on_delete=models.CASCADE)),
                ('studentID', models.ForeignKey(to='Students.Student', verbose_name='the related student',on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='StudentConfigParams',
            fields=[
                ('scpID', models.AutoField(primary_key=True, serialize=False)),
                ('displayBadges', models.BooleanField(default=False)),
                ('displayLeaderBoard', models.BooleanField(default=False)),
                ('displayClassSkills', models.BooleanField(default=False)),
                ('displayClassAverage', models.BooleanField(default=False)),
                ('displayClassRanking', models.BooleanField(default=False)),
                ('courseID', models.ForeignKey(to='Instructors.Courses', verbose_name='the related course',on_delete=models.CASCADE)),
                ('studentID', models.ForeignKey(to='Students.Student', verbose_name='the related student',on_delete=models.CASCADE)),
            ],
        ),
    ]
