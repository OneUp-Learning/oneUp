# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-09-03 01:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0035_studentchallengequestions_seed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='avaterImage',
        ),
    ]