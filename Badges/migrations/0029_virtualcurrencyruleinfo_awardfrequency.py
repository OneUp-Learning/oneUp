# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-01-15 05:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0028_remove_virtualcurrencyruleinfo_awardfrequency'),
    ]

    operations = [
        migrations.AddField(
            model_name='virtualcurrencyruleinfo',
            name='awardFrequency',
            field=models.IntegerField(default=1100),
        ),
    ]
