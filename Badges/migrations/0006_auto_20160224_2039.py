# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0005_auto_20160129_2006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actionarguments',
            name='sequenceNumber',
            field=models.IntegerField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='badges',
            name='assignToChallenges',
            field=models.IntegerField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='conditions',
            name='operand1Type',
            field=models.IntegerField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='conditions',
            name='operand1Value',
            field=models.IntegerField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='conditions',
            name='operand2Type',
            field=models.IntegerField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='conditions',
            name='operand2Value',
            field=models.IntegerField(),
            preserve_default=True,
        ),
    ]
