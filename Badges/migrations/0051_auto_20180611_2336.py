# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-06-12 03:36

# Modified by Keith Irwin to add the copy_award_frequency python code.

from __future__ import unicode_literals

from django.db import migrations, models

def copy_award_frequency(apps,schema_editor):
    VirtualCurrencyRuleInfo = apps.get_model("Badges","VirtualCurrencyRuleInfo")
    for vcRuleInfo in VirtualCurrencyRuleInfo.objects.all():
        vcRuleInfo.ruleID.awardFrequency = vcRuleInfo.awardFrequency

class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0050_courseconfigparams_courseavailable'),
    ]

    operations = [
        migrations.AddField(
            model_name='rules',
            name='awardFrequency',
            field=models.IntegerField(default=1100),
        ),
        migrations.AddField(
            model_name='rules',
            name='objectSpecifier',
            field=models.CharField(default='[]', max_length=2000, verbose_name='A json-serialized object of the type ChosenObjectSpecifier (see events.py)'),
        ),
#        migrations.RunPython(copy_award_frequency),
# This worked at the time it was run, but doesn't seem to work now,
# for some reason.
    ]
