# Generated by Django 2.0.8 on 2019-01-18 14:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0093_attendancestreak_virtualcurrencyawarded'),
        ('Students', '0070_auto_20190110_2025'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentStreaks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('streakStartDate', models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='The date the streak reset on')),
                ('streakType', models.IntegerField(default=0)),
                ('completedStreakCount', models.IntegerField(default=0)),
                ('courseID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Instructors.Courses', verbose_name='the related course')),
                ('studentID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Students.Student', verbose_name='the related student')),
            ],
        ),
    ]
