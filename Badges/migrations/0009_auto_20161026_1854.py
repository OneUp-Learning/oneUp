# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0013_merge_20161021_1451'),
        ('Instructors', '0025_auto_20161026_1854'),
        ('Badges', '0008_courseconfigparams_studentconfigparams'),
    ]

    operations = [
        migrations.CreateModel(
            name='Leaderboards',
            fields=[
                ('leaderboardID', models.AutoField(serialize=False, primary_key=True)),
                ('courseID', models.ForeignKey(to='Instructors.Courses', verbose_name='Course Name',on_delete=models.CASCADE)),
                ('studentID', models.ForeignKey(to='Students.Student', verbose_name='the related student',on_delete=models.CASCADE)),
            ],
        ),
        migrations.RenameField(
            model_name='courseconfigparams',
            old_name='leaderBoardUsed',
            new_name='leaderboardUsed',
        ),
        migrations.RenameField(
            model_name='courseconfigparams',
            old_name='levellingUsed',
            new_name='levelingUsed',
        ),
        migrations.RenameField(
            model_name='courseconfigparams',
            old_name='numStudentBestSkillsUsed',
            new_name='numStudentBestSkillsDisplayed',
        ),
        migrations.RenameField(
            model_name='courseconfigparams',
            old_name='numStudentToppersUsed',
            new_name='numStudentToppersDisplayed',
        ),
        migrations.RenameField(
            model_name='studentconfigparams',
            old_name='latestBadgesDisplayed',
            new_name='displayBadges',
        ),
        migrations.RenameField(
            model_name='studentconfigparams',
            old_name='classAverageDisplayed',
            new_name='displayClassAverage',
        ),
        migrations.RenameField(
            model_name='studentconfigparams',
            old_name='classRankingDisplayed',
            new_name='displayClassRanking',
        ),
        migrations.RenameField(
            model_name='studentconfigparams',
            old_name='studentBestSkillsDisplayed',
            new_name='displayClassSkills',
        ),
        migrations.RenameField(
            model_name='studentconfigparams',
            old_name='leaderBoardDisplayed',
            new_name='displayLeaderBoard',
        ),
        migrations.RemoveField(
            model_name='courseconfigparams',
            name='latestBadgesUsed',
        ),
        migrations.RemoveField(
            model_name='studentconfigparams',
            name='avatarDisplayed',
        ),
        migrations.RemoveField(
            model_name='studentconfigparams',
            name='levellingDisplayed',
        ),
        migrations.RemoveField(
            model_name='studentconfigparams',
            name='studentToppersDisplayed',
        ),
        migrations.RemoveField(
            model_name='studentconfigparams',
            name='virtualCurrencyDisplayed',
        ),
        migrations.AddField(
            model_name='courseconfigparams',
            name='classRankingDisplayed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='courseconfigparams',
            name='classSkillsDisplayed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='courseconfigparams',
            name='courseEndDate',
            field=models.DateField(default=datetime.datetime(1, 1, 1, 0, 0)),
        ),
        migrations.AddField(
            model_name='courseconfigparams',
            name='courseStartDate',
            field=models.DateField(default=datetime.datetime(1, 1, 1, 0, 0)),
        ),
        migrations.AddField(
            model_name='courseconfigparams',
            name='leaderBoardUpdateFreq',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='courseconfigparams',
            name='studCanChangeBadgeVis',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='courseconfigparams',
            name='studCanChangeClassRankingVis',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='courseconfigparams',
            name='studCanChangeClassSkillsVis',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='courseconfigparams',
            name='studCanChangeLeaderboardVis',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='courseconfigparams',
            name='studCanChangeclassAverageVis',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='studentconfigparams',
            name='studentID',
            field=models.ForeignKey(verbose_name='the related student', default=0, to='Students.Student',on_delete=models.CASCADE),
            preserve_default=False,
        ),
    ]
