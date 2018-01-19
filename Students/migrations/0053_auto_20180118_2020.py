# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-01-18 20:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0052_auto_20180114_0553'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentvirtualcurrency',
            name='vcRuleID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Badges.VirtualCurrencyCustomRuleInfo', verbose_name='the virtual currency rule'),
        ),
    ]
