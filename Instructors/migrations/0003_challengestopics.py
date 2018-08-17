# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0002_auto_20151001_2057'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChallengesTopics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('challengeID', models.ForeignKey(verbose_name=b'challenges', to='Instructors.Challenges',on_delete=models.CASCADE)),
                ('topicID', models.ForeignKey(verbose_name=b'topic', to='Instructors.Topics',on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
