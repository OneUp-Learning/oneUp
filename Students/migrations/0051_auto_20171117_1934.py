# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-11-17 19:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0050_auto_20171115_1907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentactivities',
            name='activityScore',
            field=models.DecimalField(decimal_places=0, max_digits=6),
        ),
    ]