# Generated by Django 2.1.2 on 2021-10-03 02:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0136_auto_20210926_2110'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='instructorregisteredcourses',
            name='Donations',
        ),
        migrations.AddField(
            model_name='courses',
            name='Donations',
            field=models.IntegerField(default=0),
        ),
    ]