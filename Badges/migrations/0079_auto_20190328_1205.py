# Generated by Django 2.1.2 on 2019-03-28 16:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0104_auto_20190128_2201'),
        ('Badges', '0078_courseconfigparams_vcduelmaxbet'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AttendaceStreakConfiguration',
            new_name='AttendanceStreakConfiguration',
        ),
    ]