# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-07-24 05:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0052_remove_virtualcurrencyruleinfo_awardfrequency'),
    ]

    operations = [
        migrations.AddField(
            model_name='ruleevents',
            name='inGlobalContext',
            field=models.BooleanField(default=True),
        ),
    ]