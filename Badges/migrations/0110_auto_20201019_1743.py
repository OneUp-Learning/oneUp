# Generated by Django 2.2.4 on 2020-10-19 21:43

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0109_courseconfigparams_flashcardsused'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseconfigparams',
            name='maxNumberOfTeamStudents',
            field=models.IntegerField(default=3),
        ),
        migrations.AddField(
            model_name='courseconfigparams',
            name='teamsEnabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='courseconfigparams',
            name='teamsLockInDeadline',
            field=models.DateTimeField(default=datetime.datetime(2020, 10, 26, 21, 42, 59, tzinfo=utc), verbose_name='Deadline for team members to be locked in to the team'),
        ),
    ]
