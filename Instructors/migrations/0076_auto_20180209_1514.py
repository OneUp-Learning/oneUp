# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-02-09 20:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0075_auto_20180203_1423'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenges',
            name='curve',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
        migrations.AddField(
            model_name='challenges',
            name='totalScore',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
    ]