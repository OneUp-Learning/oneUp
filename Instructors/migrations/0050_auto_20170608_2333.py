# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-06-08 23:33
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0049_auto_20170523_0012'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='depenentLibrary',
            new_name='dependentLibrary',
        ),
        migrations.RenameField(
            model_name='dependentlibrary',
            old_name='mainLibary',
            new_name='mainLibrary',
        ),
        migrations.RenameField(
            model_name='lualibrary',
            old_name='libarayName',
            new_name='libraryName',
        ),
    ]
