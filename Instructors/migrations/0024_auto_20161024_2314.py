# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Instructors', '0023_auto_20160921_2109'),
    ]

    operations = [
        migrations.CreateModel(
            name='Avatars',
            fields=[
                ('avatarID', models.AutoField(primary_key=True, serialize=False)),
                ('courseID', models.ForeignKey(verbose_name='Course Name', to='Instructors.Courses')),
            ],
        ),
        migrations.CreateModel(
            name='Leaderboards',
            fields=[
                ('leaderboardID', models.AutoField(primary_key=True, serialize=False)),
                ('avatarID', models.ForeignKey(verbose_name='Author', to=settings.AUTH_USER_MODEL)),
                ('courseID', models.ForeignKey(verbose_name='Course Name', to='Instructors.Courses')),
            ],
        ),
        migrations.RemoveField(
            model_name='courseconfigparams',
            name='courseID',
        ),
        migrations.DeleteModel(
            name='CourseConfigParams',
        ),
    ]
