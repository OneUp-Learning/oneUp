# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-24 19:43
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Instructors', '0049_auto_20170523_0012'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedFiles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uploadedFile', models.FileField(max_length=500, upload_to='D:\\workspace\\oneUpER\\media\\textfiles/xmlfiles')),
                ('uploadedFileName', models.CharField(default='', max_length=200)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('uploadedFileCreator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Creator')),
            ],
        ),
        migrations.AlterField(
            model_name='lualibrary',
            name='libFile',
            field=models.FileField(max_length=5000, upload_to='D:\\workspace\\oneUpER\\media\\lua/uploadedLuaLibs'),
        ),
        migrations.AlterField(
            model_name='uploadedimages',
            name='imageFile',
            field=models.FileField(max_length=500, upload_to='D:\\workspace\\oneUpER\\media\\images/uploadedInstructorImages'),
        ),
    ]
