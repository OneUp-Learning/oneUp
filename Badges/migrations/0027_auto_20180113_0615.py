# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-01-13 06:15
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0026_auto_20180112_2356'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='virtualcurrencyawardrecord',
            name='vcRule',
        ),
        migrations.DeleteModel(
            name='VirtualCurrencyAwardRecord',
        ),
    ]
