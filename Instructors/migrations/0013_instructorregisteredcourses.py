# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Instructors', '0012_auto_20160219_2029'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstructorRegisteredCourses',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('courseID', models.ForeignKey(to='Instructors.Courses', verbose_name='Course Name', on_delete=models.CASCADE )),
                ('instructorID', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Instructor ID', on_delete=models.CASCADE )),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
