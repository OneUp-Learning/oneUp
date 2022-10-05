# Generated by Django 2.1.2 on 2021-12-01 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0142_auto_20211201_0933'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='triviaquestion',
            name='maximumPointsPossible',
        ),
        migrations.RemoveField(
            model_name='triviaquestion',
            name='maximumVCPossible',
        ),
        migrations.AddField(
            model_name='trivia',
            name='maximumPointsPerQuestion',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='trivia',
            name='maximumVCPossible',
            field=models.IntegerField(default=0),
        ),
    ]