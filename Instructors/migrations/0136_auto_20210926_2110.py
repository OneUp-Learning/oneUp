# Generated by Django 2.1.2 on 2021-09-27 01:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0135_auto_20210926_1914'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instructorregisteredcourses',
            name='Donations',
            field=models.IntegerField(default=0),
        ),
    ]
