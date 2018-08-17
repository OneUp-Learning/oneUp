# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Instructors', '0004_instructors'),
    ]

    operations = [
        migrations.CreateModel(
            name='Announcements',
            fields=[
                ('announcementID', models.AutoField(primary_key=True, serialize=False)),
                ('startTimestamp', models.DateTimeField()),
                ('endTimestamp', models.DateTimeField()),
                ('message', models.CharField(max_length=300)),
                ('authorID', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Author',on_delete=models.CASCADE)),
                ('courseID', models.ForeignKey(to='Instructors.Courses', verbose_name='Course Name',on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='challengestopics',
            name='challengeID',
            field=models.ForeignKey(to='Instructors.Challenges', verbose_name='challenges',on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='challengestopics',
            name='topicID',
            field=models.ForeignKey(to='Instructors.Topics', verbose_name='topic',on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='coursestopics',
            name='courseID',
            field=models.ForeignKey(to='Instructors.Courses', verbose_name='courses',on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='coursestopics',
            name='topicID',
            field=models.ForeignKey(to='Instructors.Topics', verbose_name='topic',on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
