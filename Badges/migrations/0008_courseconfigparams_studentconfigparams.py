# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0024_auto_20161024_2314'),
        ('Badges', '0007_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseConfigParams',
            fields=[
                ('ccpID', models.AutoField(primary_key=True, serialize=False)),
                ('badgesUsed', models.BooleanField(default=False)),
                ('latestBadgesUsed', models.BooleanField(default=False)),
                ('levellingUsed', models.BooleanField(default=False)),
                ('leaderBoardUsed', models.BooleanField(default=False)),
                ('virtualCurrencyUsed', models.BooleanField(default=False)),
                ('avatarUsed', models.BooleanField(default=False)),
                ('classAverageUsed', models.BooleanField(default=False)),
                ('numStudentToppersUsed', models.IntegerField(default=0)),
                ('numStudentBestSkillsUsed', models.IntegerField(default=0)),
                ('courseID', models.ForeignKey(verbose_name='the related course', to='Instructors.Courses',on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='StudentConfigParams',
            fields=[
                ('scpID', models.AutoField(primary_key=True, serialize=False)),
                ('latestBadgesDisplayed', models.BooleanField(default=False)),
                ('levellingDisplayed', models.BooleanField(default=False)),
                ('leaderBoardDisplayed', models.BooleanField(default=False)),
                ('virtualCurrencyDisplayed', models.BooleanField(default=False)),
                ('avatarDisplayed', models.BooleanField(default=False)),
                ('classAverageDisplayed', models.BooleanField(default=False)),
                ('studentToppersDisplayed', models.BooleanField(default=False)),
                ('studentBestSkillsDisplayed', models.BooleanField(default=False)),
                ('classRankingDisplayed', models.BooleanField(default=False)),
                ('ccpID', models.ForeignKey(verbose_name='course config parameter ID', to='Badges.CourseConfigParams',on_delete=models.CASCADE)),
                ('courseID', models.ForeignKey(verbose_name='the related course', to='Instructors.Courses',on_delete=models.CASCADE)),
            ],
        ),
    ]
