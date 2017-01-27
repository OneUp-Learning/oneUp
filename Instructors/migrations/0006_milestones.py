# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Instructors', '0005_auto_20151029_1723'),
    ]

    operations = [
        migrations.CreateModel(
            name='Milestones',
            fields=[
                ('milestoneID', models.AutoField(serialize=False, primary_key=True)),
                ('milestoneName', models.CharField(max_length=75)),
                ('description', models.CharField(max_length=200)),
                ('points', models.IntegerField(max_length=5)),
                ('authorID', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Author')),
                ('courseID', models.ForeignKey(to='Instructors.Courses', verbose_name='Course Name')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
