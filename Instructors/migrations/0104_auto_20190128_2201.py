# Generated by Django 2.0.8 on 2019-01-29 03:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0103_auto_20190125_1515'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendacestreakconfiguration',
            name='courseID',
        ),
        migrations.DeleteModel(
            name='AttendaceStreakConfiguration',
        ),
    ]
