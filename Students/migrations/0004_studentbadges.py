# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0001_initial'),
        ('Students', '0003_auto_20150421_1709'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentBadges',
            fields=[
                ('studentBadgeID', models.AutoField(serialize=False, primary_key=True)),
                ('badgeID', models.ForeignKey(to='Badges.Badges', verbose_name='the badge',on_delete=models.CASCADE)),
                ('studentID', models.ForeignKey(to='Students.Student', verbose_name='the student',on_delete=models.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
