# Generated by Django 2.1.2 on 2022-02-25 17:49

import Students.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0140_auto_20211021_1448'),
        ('Students', '0115_auto_20211014_1439'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentActivitySubmission',
            fields=[
                ('studentSubmissionID', models.AutoField(primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(default=Students.models.custom_now)),
                ('richTextSubmission', models.CharField(blank=True, max_length=20000, null=True)),
                ('comment', models.CharField(default='', max_length=500)),
                ('latest', models.BooleanField(default=True)),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Students.StudentActivities', verbose_name='the related activity')),
                ('courseID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Instructors.Courses', verbose_name='the related course')),
                ('studentID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Students.Student', verbose_name='the related student')),
            ],
        ),
    ]