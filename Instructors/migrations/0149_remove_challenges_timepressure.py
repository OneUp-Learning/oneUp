# Generated by Django 2.1.2 on 2022-11-23 19:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0148_challenges_timepressure'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='challenges',
            name='timePressure',
        ),
    ]