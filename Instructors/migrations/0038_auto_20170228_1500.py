# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-28 20:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0037_auto_20170227_1539'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadedimages',
            name='imageFile',
            field=models.FileField(max_length=500, upload_to='D:\\workspace\\oneUp\\media\\images/uploadedInstructorImages'),
        ),
    ]
