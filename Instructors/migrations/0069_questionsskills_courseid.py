# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-12-01 00:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0068_auto_20171119_1632'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionsskills',
            name='courseID',
            field=models.ForeignKey(null=True,default="", on_delete=django.db.models.deletion.CASCADE, to='Instructors.Courses', verbose_name='courses'),
        ),
    ]
