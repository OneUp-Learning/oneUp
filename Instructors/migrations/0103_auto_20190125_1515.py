# Generated by Django 2.0.8 on 2019-01-25 20:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0102_auto_20190123_2221'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='streaks',
            name='courseID',
        ),
        migrations.DeleteModel(
            name='Streaks',
        ),
    ]