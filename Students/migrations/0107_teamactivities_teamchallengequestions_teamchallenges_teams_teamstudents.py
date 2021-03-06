# Generated by Django 2.2.4 on 2020-10-19 21:43

import Students.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0129_challenges_isteamchallenge'),
        ('Students', '0106_auto_20200708_1326'),
    ]

    operations = [
        migrations.CreateModel(
            name='Teams',
            fields=[
                ('teamID', models.AutoField(primary_key=True, serialize=False)),
                ('teamName', models.CharField(default='', max_length=100)),
                ('avatarImage', models.CharField(default='', max_length=200)),
                ('courseID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Instructors.Courses', verbose_name='the course')),
                ('teamLeader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Students.Student', verbose_name="the team's leader")),
            ],
        ),
        migrations.CreateModel(
            name='TeamStudents',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('studentID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Students.Student', verbose_name='the student')),
                ('teamID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Students.Teams', verbose_name='the team')),
            ],
        ),
        migrations.CreateModel(
            name='TeamChallenges',
            fields=[
                ('teamChallengeID', models.AutoField(primary_key=True, serialize=False)),
                ('startTimestamp', models.DateTimeField(default=Students.models.custom_now)),
                ('endTimestamp', models.DateTimeField(default=Students.models.custom_now)),
                ('testScore', models.DecimalField(decimal_places=2, max_digits=6)),
                ('scoreAdjustment', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('adjustmentReason', models.CharField(default='', max_length=1000)),
                ('instructorFeedback', models.CharField(max_length=200)),
                ('challengeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Instructors.Challenges', verbose_name='the related challenge')),
                ('courseID', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='Instructors.Courses', verbose_name='the related course')),
                ('teamID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Students.Teams', verbose_name='the related team')),
            ],
        ),
        migrations.CreateModel(
            name='TeamChallengeQuestions',
            fields=[
                ('teamChallengeQuestionID', models.AutoField(primary_key=True, serialize=False)),
                ('questionScore', models.DecimalField(decimal_places=2, max_digits=6)),
                ('questionTotal', models.DecimalField(decimal_places=2, max_digits=6)),
                ('instructorFeedback', models.CharField(max_length=200)),
                ('seed', models.IntegerField(default=0)),
                ('challengeQuestionID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Instructors.ChallengesQuestions', verbose_name='the related challenge question')),
                ('questionID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Instructors.Questions', verbose_name='the related question')),
                ('teamChallengeID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Students.TeamChallenges', verbose_name='the related team challenge')),
            ],
        ),
        migrations.CreateModel(
            name='TeamActivities',
            fields=[
                ('teamActivityID', models.AutoField(primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(default=Students.models.custom_now, verbose_name='Grading Timestamp')),
                ('hasTimestamp', models.BooleanField(default=False)),
                ('submissionTimestamp', models.DateTimeField(default=Students.models.custom_now, verbose_name='Latest submission timestamp')),
                ('submitted', models.BooleanField(default=False)),
                ('activityScore', models.DecimalField(decimal_places=0, max_digits=6)),
                ('instructorFeedback', models.CharField(default='', max_length=200)),
                ('graded', models.BooleanField(default=False)),
                ('numOfUploads', models.IntegerField(default=0)),
                ('comment', models.CharField(default='', max_length=500)),
                ('activityID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Instructors.Activities', verbose_name='the related activity')),
                ('courseID', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='Instructors.Courses', verbose_name='Course Name')),
                ('teamID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Students.Student', verbose_name='the related team')),
            ],
        ),
    ]
