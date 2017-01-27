# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0024_auto_20161024_2314'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='avatars',
            name='courseID',
        ),
        migrations.RemoveField(
            model_name='leaderboards',
            name='avatarID',
        ),
        migrations.RemoveField(
            model_name='leaderboards',
            name='courseID',
        ),
        migrations.DeleteModel(
            name='Avatars',
        ),
        migrations.DeleteModel(
            name='Leaderboards',
        ),
    ]
