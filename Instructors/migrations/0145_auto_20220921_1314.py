# Generated by Django 2.2.4 on 2022-09-21 17:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0144_trivia_currentlyrunning'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='triviaquestion',
            name='challengeQuestion',
        ),
        migrations.AddField(
            model_name='triviaquestion',
            name='maxPoints',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='triviaquestion',
            name='questionText',
            field=models.CharField(default='', max_length=5000),
        ),
        migrations.CreateModel(
            name='TriviaAnswer',
            fields=[
                ('answerID', models.AutoField(primary_key=True, serialize=False)),
                ('answerText', models.CharField(max_length=5000)),
                ('isCorrect', models.BooleanField(default=False)),
                ('questionID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Instructors.TriviaQuestion', verbose_name='Linked Trivia Question')),
            ],
        ),
    ]