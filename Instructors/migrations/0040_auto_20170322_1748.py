# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-22 21:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0039_auto_20170301_0652'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedimages',
            name='imageFile',
            field=models.FileField(max_length=500, upload_to='C:\\Users\\austin\\Documents\\Workspaces\\oneUp\\media\\images/uploadedInstructorImages'),
        ),
    ]
