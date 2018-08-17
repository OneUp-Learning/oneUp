# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0013_instructorregisteredcourses'),
        ('Students', '0009_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentRegisteredCourses',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('courseID', models.ForeignKey(to='Instructors.Courses', verbose_name='the related course', default=1,on_delete=models.CASCADE)),
                ('studentID', models.ForeignKey(to='Students.Student', verbose_name='the related student',on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
