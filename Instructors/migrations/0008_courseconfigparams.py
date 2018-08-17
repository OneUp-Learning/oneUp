# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0007_announcements_subject'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseConfigParams',
            fields=[
                ('ccpID', models.AutoField(primary_key=True, serialize=False)),
                ('courseAuthor', models.CharField(max_length=75)),
                ('courseBucks', models.BooleanField(default=False)),
                ('isClassAverageDisplayed', models.BooleanField(default=False)),
                ('courseID', models.ForeignKey(verbose_name='course', to='Instructors.Courses',on_delete=models.CASCADE )),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
 
