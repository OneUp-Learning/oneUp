# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-05-14 20:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0038_badgesinfo'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='BadgesInfo',
            new_name='BadgesManual',
        ),
    ]
