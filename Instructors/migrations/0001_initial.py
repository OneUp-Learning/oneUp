# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Activities',
            fields=[
                ('activityID', models.AutoField(primary_key=True, serialize=False)),
                ('activityName', models.CharField(max_length=75)),
                ('description', models.CharField(max_length=200)),
                ('points', models.IntegerField(max_length=5)),
                ('instructorNotes', models.CharField(max_length=300)),
                ('author', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Answers',
            fields=[
                ('answerID', models.AutoField(primary_key=True, serialize=False)),
                ('answerText', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Challenges',
            fields=[
                ('challengeID', models.AutoField(primary_key=True, serialize=False)),
                ('challengeName', models.CharField(max_length=100)),
                ('challengeCategory', models.CharField(max_length=100)),
                ('isGraded', models.BooleanField(default=False)),
                ('numberAttempts', models.IntegerField(max_length=5)),
                ('timeLimit', models.IntegerField(max_length=5)),
                ('feedbackOption', models.IntegerField(max_length=5)),
                ('challengeAuthor', models.CharField(max_length=75)),
                ('challengeDifficulty', models.CharField(max_length=45)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ChallengesQuestions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('points', models.IntegerField(max_length=5)),
                ('challengeID', models.ForeignKey(verbose_name='challenge', to='Instructors.Challenges')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ChallengeTags',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('challengeID', models.ForeignKey(verbose_name='challenge', to='Instructors.Challenges')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CodeLibrary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('fileName', models.CharField(max_length=1000)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CorrectAnswers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('answerID', models.ForeignKey(verbose_name='the correct answer', to='Instructors.Answers')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Courses',
            fields=[
                ('courseID', models.AutoField(primary_key=True, serialize=False)),
                ('courseName', models.CharField(max_length=75)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CoursesSkills',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('courseID', models.ForeignKey(verbose_name='courses', to='Instructors.Courses')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Difficulty',
            fields=[
                ('difficultyID', models.AutoField(primary_key=True, serialize=False)),
                ('difficulty', models.CharField(max_length=75)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FeedbackType',
            fields=[
                ('feedbackID', models.AutoField(primary_key=True, serialize=False)),
                ('feedbackText', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Goals',
            fields=[
                ('goalID', models.AutoField(primary_key=True, serialize=False)),
                ('goalAuthor', models.CharField(max_length=75)),
                ('goalsCol', models.CharField(max_length=75)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MatchingAnswers',
            fields=[
                ('matchingAnswerID', models.AutoField(primary_key=True, serialize=False)),
                ('matchingAnswerText', models.CharField(max_length=100)),
                ('answerID', models.ForeignKey(verbose_name='the related question', to='Instructors.Answers')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Prompts',
            fields=[
                ('promptID', models.AutoField(primary_key=True, serialize=False)),
                ('promptText', models.CharField(max_length=100)),
                ('answerID', models.ForeignKey(verbose_name='the correct answer for this prompt', to='Instructors.Answers')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Questions',
            fields=[
                ('questionID', models.AutoField(primary_key=True, serialize=False)),
                ('preview', models.CharField(max_length=200)),
                ('instructorNotes', models.CharField(max_length=300)),
                ('difficulty', models.CharField(max_length=50)),
                ('author', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DynamicQuestions',
            fields=[
                ('questions_ptr', models.OneToOneField(parent_link=True, to='Instructors.Questions', serialize=False, primary_key=True, auto_created=True)),
                ('code', models.CharField(max_length=10000)),
            ],
            options={
            },
            bases=('Instructors.questions',),
        ),
        migrations.CreateModel(
            name='QuestionsSkills',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('questionSkillPoints', models.IntegerField(max_length=5, default=1)),
                ('challengeID', models.ForeignKey(verbose_name='challenges', to='Instructors.Challenges')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuestionTypes',
            fields=[
                ('typeID', models.AutoField(primary_key=True, serialize=False)),
                ('typeName', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResourceTags',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Skills',
            fields=[
                ('skillID', models.AutoField(primary_key=True, serialize=False)),
                ('skillName', models.CharField(max_length=100)),
                ('skillAuthor', models.CharField(max_length=75)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StaticQuestions',
            fields=[
                ('questions_ptr', models.OneToOneField(parent_link=True, to='Instructors.Questions', serialize=False, primary_key=True, auto_created=True)),
                ('questionText', models.CharField(max_length=1000)),
                ('correctAnswerFeedback', models.CharField(max_length=200)),
                ('incorrectAnswerFeedback', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=('Instructors.questions',),
        ),
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('tagID', models.AutoField(primary_key=True, serialize=False)),
                ('tagName', models.CharField(max_length=75)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='resourcetags',
            name='questionID',
            field=models.ForeignKey(verbose_name='question', to='Instructors.Questions'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resourcetags',
            name='tagID',
            field=models.ForeignKey(verbose_name='tag', to='Instructors.Tags'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='questionsskills',
            name='questionID',
            field=models.ForeignKey(verbose_name='questions', to='Instructors.Questions'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='questionsskills',
            name='skillID',
            field=models.ForeignKey(verbose_name='skill', to='Instructors.Skills'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='questions',
            name='type',
            field=models.ForeignKey(verbose_name='the type of the question', to='Instructors.QuestionTypes'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='prompts',
            name='questionID',
            field=models.ForeignKey(verbose_name='the related question', to='Instructors.Questions'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='matchinganswers',
            name='questionID',
            field=models.ForeignKey(verbose_name='the related question', to='Instructors.Questions'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='coursesskills',
            name='skillID',
            field=models.ForeignKey(verbose_name='skill', to='Instructors.Skills'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='correctanswers',
            name='questionID',
            field=models.ForeignKey(verbose_name='the question', to='Instructors.Questions'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='challengetags',
            name='tagID',
            field=models.ForeignKey(verbose_name='tag', to='Instructors.Tags'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='challengesquestions',
            name='questionID',
            field=models.ForeignKey(verbose_name='question', to='Instructors.Questions'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='challenges',
            name='courseID',
            field=models.ForeignKey(verbose_name='the related course', to='Instructors.Courses'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='answers',
            name='questionID',
            field=models.ForeignKey(verbose_name='the related question', to='Instructors.Questions'),
            preserve_default=True,
        ),
    ]
