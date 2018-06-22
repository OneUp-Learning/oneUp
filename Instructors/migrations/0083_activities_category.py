# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-04-20 19:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0082_activitiescategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='activities',
            name='category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='Instructors.ActivitiesCategory', verbose_name='Activities Category'),
        ),
    ]