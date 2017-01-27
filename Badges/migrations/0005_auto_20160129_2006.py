# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0004_auto_20151217_2019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actionarguments',
            name='sequenceNumber',
            field=models.IntegerField(max_length=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='badges',
            name='assignToChallenges',
            field=models.IntegerField(max_length=1),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='conditions',
            name='operand1Type',
            field=models.IntegerField(max_length=1),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='conditions',
            name='operand1Value',
            field=models.IntegerField(max_length=5),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='conditions',
            name='operand2Type',
            field=models.IntegerField(max_length=1),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='conditions',
            name='operand2Value',
            field=models.IntegerField(max_length=5),
            preserve_default=True,
        ),
    ]
