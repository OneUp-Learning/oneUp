# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-13 17:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0045_auto_20170410_1528'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedimages',
            name='imageFile',
            field=models.FileField(max_length=500, upload_to='D:\\workspace\\oneUpER\\media\\images/uploadedInstructorImages'),
        ),
    ]
