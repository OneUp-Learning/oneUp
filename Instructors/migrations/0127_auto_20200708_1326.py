# Generated by Django 2.2.4 on 2020-07-08 17:26

import Instructors.models
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0126_flashcardtogroup_flashid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activities',
            name='deadLine',
            field=models.DateTimeField(blank=True, default=Instructors.models.custom_now),
        ),
        migrations.AlterField(
            model_name='activities',
            name='endTimestamp',
            field=models.DateTimeField(blank=True, default=Instructors.models.custom_now),
        ),
        migrations.AlterField(
            model_name='activities',
            name='startTimestamp',
            field=models.DateTimeField(blank=True, default=Instructors.models.custom_now),
        ),
        migrations.AlterField(
            model_name='announcements',
            name='endTimestamp',
            field=models.DateTimeField(default=Instructors.models.custom_now),
        ),
        migrations.AlterField(
            model_name='announcements',
            name='startTimestamp',
            field=models.DateTimeField(default=Instructors.models.custom_now),
        ),
        migrations.AlterField(
            model_name='challenges',
            name='dueDate',
            field=models.DateTimeField(blank=True, default=Instructors.models.custom_now),
        ),
        migrations.AlterField(
            model_name='challenges',
            name='endTimestamp',
            field=models.DateTimeField(blank=True, default=Instructors.models.custom_now),
        ),
        migrations.AlterField(
            model_name='challenges',
            name='startTimestamp',
            field=models.DateTimeField(blank=True, default=Instructors.models.custom_now),
        ),
        migrations.AlterField(
            model_name='flashcardgroupcourse',
            name='availabilityDate',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='questionprogrammingfiles',
            name='uploaded_at',
            field=models.DateTimeField(default=Instructors.models.custom_now),
        ),
        migrations.AlterField(
            model_name='uploadedactivityfiles',
            name='uploaded_at',
            field=models.DateTimeField(default=Instructors.models.custom_now),
        ),
        migrations.AlterField(
            model_name='uploadedfiles',
            name='uploaded_at',
            field=models.DateTimeField(default=Instructors.models.custom_now),
        ),
    ]