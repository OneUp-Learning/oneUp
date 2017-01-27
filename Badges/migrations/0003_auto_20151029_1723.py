# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0002_actions_events_systemvariables'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Actions',
        ),
        migrations.DeleteModel(
            name='Events',
        ),
        migrations.DeleteModel(
            name='SystemVariables',
        ),
    ]
