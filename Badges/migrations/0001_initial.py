# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActionArguments',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('sequenceNumber', models.IntegerField(max_length=5)),
                ('argumentValue', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BadgeChallenges',
            fields=[
                ('badgeChallengeID', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Badges',
            fields=[
                ('badgeID', models.AutoField(primary_key=True, serialize=False)),
                ('badgeName', models.CharField(max_length=30)),
                ('badgeDescription', models.CharField(max_length=100)),
                ('badgeImage', models.CharField(max_length=30)),
                ('assignToChallenges', models.IntegerField(max_length=1)),
                ('courseID', models.ForeignKey(verbose_name='the related course', to='Instructors.Courses')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Conditions',
            fields=[
                ('conditionID', models.AutoField(primary_key=True, serialize=False)),
                ('operation', models.CharField(max_length=100)),
                ('operand1Type', models.IntegerField(max_length=1)),
                ('operand1Value', models.IntegerField(max_length=5)),
                ('operand2Type', models.IntegerField(max_length=1)),
                ('operand2Value', models.IntegerField(max_length=5)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourseMechanics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('courseID', models.ForeignKey(verbose_name='the related course', to='Instructors.Courses')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Dates',
            fields=[
                ('dateID', models.AutoField(primary_key=True, serialize=False)),
                ('dateValue', models.DateField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FloatConstants',
            fields=[
                ('floatID', models.AutoField(primary_key=True, serialize=False)),
                ('floatValue', models.DecimalField(max_digits=6, decimal_places=2)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GameMechanics',
            fields=[
                ('gameMechanismID', models.AutoField(primary_key=True, serialize=False)),
                ('gameMechanismName', models.CharField(max_length=30)),
                ('gameMechanismDescription', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rules',
            fields=[
                ('ruleID', models.AutoField(primary_key=True, serialize=False)),
                ('eventID', models.IntegerField(verbose_name='the related event', db_index=True)),
                ('actionID', models.IntegerField(verbose_name='the related action', db_index=True)),
                ('conditionID', models.ForeignKey(verbose_name='the related condition', to='Badges.Conditions')),
                ('courseID', models.ForeignKey(verbose_name='Course the rule belongs to', to='Instructors.Courses')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StringConstants',
            fields=[
                ('stringID', models.AutoField(primary_key=True, serialize=False)),
                ('stringValue', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='coursemechanics',
            name='gameMechanismID',
            field=models.ForeignKey(verbose_name='the related game mechanism', to='Badges.GameMechanics'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='badges',
            name='ruleID',
            field=models.ForeignKey(verbose_name='the related rule', to='Badges.Rules'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='badgechallenges',
            name='badgeID',
            field=models.ForeignKey(verbose_name='the related badge', to='Badges.Badges'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='badgechallenges',
            name='challengeID',
            field=models.ForeignKey(verbose_name='the related challenge', to='Instructors.Challenges'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='actionarguments',
            name='ruleID',
            field=models.ForeignKey(verbose_name='the related rule', to='Badges.Rules'),
            preserve_default=True,
        ),
    ]
