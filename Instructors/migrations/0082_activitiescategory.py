# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-04-20 19:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0081_activities_deadline'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivitiesCategory',
            fields=[
                ('categoryID', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=75)),
                ('courseID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Instructors.Courses', verbose_name='Course Name')),
            ],
        ),
    ]
