# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-05-16 17:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0040_activitycategoryset'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='BadgesManual',
            new_name='BadgesInfo',
        ),
    ]