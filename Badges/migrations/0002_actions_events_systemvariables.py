# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Actions',
            fields=[
                ('actionID', models.AutoField(primary_key=True, serialize=False)),
                ('actionName', models.CharField(max_length=30)),
                ('actionDescription', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Events',
            fields=[
                ('eventID', models.AutoField(primary_key=True, serialize=False)),
                ('eventName', models.CharField(max_length=30)),
                ('eventDescription', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SystemVariables',
            fields=[
                ('systemVariableID', models.AutoField(primary_key=True, serialize=False)),
                ('variableName', models.CharField(max_length=30)),
                ('variableDescription', models.CharField(max_length=100)),
                ('readOnlyIndicator', models.BooleanField(default=True)),
                ('operation', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
