# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoursesTopics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('courseID', models.ForeignKey(verbose_name=b'courses', to='Instructors.Courses',on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Topics',
            fields=[
                ('topicID', models.AutoField(serialize=False, primary_key=True)),
                ('topicName', models.CharField(max_length=100)),
                ('topicAuthor', models.CharField(max_length=75)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='coursestopics',
            name='topicID',
            field=models.ForeignKey(verbose_name=b'topic', to='Instructors.Topics',on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
