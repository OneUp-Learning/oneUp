# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-11-03 19:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0044_auto_20171015_0256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedavatarimage',
            name='avatarImage',
            field=models.FileField(max_length=500, upload_to='images/uploadedAvatarImages'),
        ),
    ]