# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-05-23 00:12
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Instructors', '0048_auto_20170421_1348'),
    ]

    operations = [
        migrations.CreateModel(
            name='depenentLibrary',
            fields=[
                ('dependID', models.AutoField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='LuaLibrary',
            fields=[
                ('libID', models.AutoField(primary_key=True, serialize=False)),
                ('libFile', models.FileField(max_length=5000, upload_to='/home/kirwin/workspace/oneUp-GIT/media/lua/uploadedLuaLibs')),
                ('libarayName', models.CharField(max_length=100)),
                ('libDescription', models.CharField(default='', max_length=200)),
                ('libCreator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Creator')),
            ],
        ),
        migrations.CreateModel(
            name='questionLibrary',
            fields=[
                ('ID', models.AutoField(primary_key=True, serialize=False)),
                ('library', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Instructors.LuaLibrary')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Instructors.Questions')),
            ],
        ),
        migrations.AlterField(
            model_name='uploadedimages',
            name='imageFile',
            field=models.FileField(max_length=500, upload_to='/home/kirwin/workspace/oneUp-GIT/media/images/uploadedInstructorImages'),
        ),
        migrations.AddField(
            model_name='depenentlibrary',
            name='dependent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Instructors.LuaLibrary'),
        ),
        migrations.AddField(
            model_name='depenentlibrary',
            name='mainLibary',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mainLibary', to='Instructors.LuaLibrary'),
        ),
    ]
