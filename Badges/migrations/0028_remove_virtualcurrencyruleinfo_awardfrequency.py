# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-01-15 05:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0027_auto_20180113_0615'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='virtualcurrencyruleinfo',
            name='awardFrequency',
        ),
    ]
