# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-12-01 00:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion

def fill_courseID(apps, schema_editor):
    # We can't import the QuestionSkills model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    QuestionSkills = apps.get_model('Instructors', 'questionsskills')
    for question in QuestionSkills.objects.all():
        course = question.challengeID.courseID
        question.courseID = course
        question.save()
        
#class Migration(migrations.Migration):

#    dependencies = [
#        ('Instructors', '0069_questionsskills_courseid'),
#    ]

#    operations = [
#        migrations.RunPython(fill_courseID),
#    ]
