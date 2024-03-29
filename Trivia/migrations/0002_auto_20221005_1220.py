# Generated by Django 2.2.4 on 2022-10-05 16:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0147_triviaquestion_questionposition'),
        ('Trivia', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='triviasession',
            name='course',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='Instructors.Courses'),
        ),
        migrations.AddField(
            model_name='triviasession',
            name='host',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='Instructors.Instructors'),
        ),
    ]
