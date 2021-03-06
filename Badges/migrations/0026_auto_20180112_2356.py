# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-01-12 23:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0070_remove_questionsskills_challengeid'),
        ('Badges', '0025_topicset'),
    ]

    operations = [
        migrations.CreateModel(
            name='VirtualCurrencyAwardRecord',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('object', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='VirtualCurrencyCustomRuleInfo',
            fields=[
                ('vcRuleID', models.AutoField(primary_key=True, serialize=False)),
                ('vcRuleName', models.CharField(max_length=30)),
                ('vcRuleDescription', models.CharField(max_length=100)),
                ('vcRuleAmount', models.IntegerField()),
                ('courseID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Instructors.Courses', verbose_name='the related course')),
            ],
        ),
        migrations.AddField(
            model_name='virtualcurrencyruleinfo',
            name='awardFrequency',
            field=models.IntegerField(default=1100),
        ),
        migrations.AddField(
            model_name='virtualcurrencyawardrecord',
            name='vcRule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Badges.VirtualCurrencyRuleInfo'),
        ),
    ]
