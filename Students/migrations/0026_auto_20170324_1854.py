# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-24 22:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0025_auto_20170322_1934'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedavatarimage',
            name='avatarImage',
            field=models.FileField(max_length=500, upload_to='C:\\Users\\austin\\Documents\\Workspaces\\oneUpER\\media\\images/uploadedAvatarImages'),
        ),
    ]
