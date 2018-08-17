# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MatchShuffledAnswers',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('MatchShuffledAnswerText', models.CharField(max_length=1000)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('universityID', models.CharField(max_length=100)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL,on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudentChallengeAnswers',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('studentAnswer', models.CharField(max_length=1000)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudentChallengeQuestions',
            fields=[
                ('studentChallengeQuestionID', models.AutoField(serialize=False, primary_key=True)),
                ('questionScore', models.DecimalField(decimal_places=2, max_digits=6)),
                ('questionTotal', models.DecimalField(decimal_places=2, max_digits=6)),
                ('usedHint', models.BooleanField(default=True)),
                ('instructorFeedback', models.CharField(max_length=200)),
                ('questionID', models.ForeignKey(verbose_name='the related question', to='Instructors.Questions',on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudentChallenges',
            fields=[
                ('studentChallengeID', models.AutoField(serialize=False, primary_key=True)),
                ('startTimestamp', models.DateTimeField()),
                ('endTimestamp', models.DateTimeField()),
                ('testScore', models.DecimalField(decimal_places=2, max_digits=6)),
                ('testTotal', models.DecimalField(decimal_places=2, max_digits=6)),
                ('instructorFeedback', models.CharField(max_length=200)),
                ('challengeID', models.ForeignKey(verbose_name='the related challenge', to='Instructors.Challenges',on_delete=models.CASCADE)),
                ('courseID', models.ForeignKey(verbose_name='the related course', to='Instructors.Courses',on_delete=models.CASCADE)),
                ('studentID', models.ForeignKey(verbose_name='the related student', to='Students.Student',on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudentCourseSkills',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('skillPoints', models.IntegerField(default=1, max_length=5)),
                ('skillID', models.ForeignKey(verbose_name='the related skill', to='Instructors.Skills',on_delete=models.CASCADE)),
                ('studentChallengeQuestionID', models.ForeignKey(verbose_name='the related student_challenge_question', to='Students.StudentChallengeQuestions',on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StudentEventLog',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('event', models.IntegerField(default=-1, verbose_name='the event which occurred', db_index=True)),
                ('timestamp', models.DateTimeField(verbose_name='timestamp', db_index=True, auto_now_add=True)),
                ('course', models.ForeignKey(verbose_name='Course in Which event occurred', to='Instructors.Courses',on_delete=models.CASCADE)),
                ('student', models.ForeignKey(verbose_name='the student', to='Students.Student',on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='studentchallengequestions',
            name='studentChallengeID',
            field=models.ForeignKey(verbose_name='the related student_challenge', to='Students.StudentChallenges',on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='studentchallengeanswers',
            name='studentChallengeQuestionID',
            field=models.ForeignKey(verbose_name='the related student_challenge_question', to='Students.StudentChallengeQuestions',on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='matchshuffledanswers',
            name='studentChallengeQuestionID',
            field=models.ForeignKey(verbose_name='the related student_challenge_question', to='Students.StudentChallengeQuestions',on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
