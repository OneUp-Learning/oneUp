# Generated by Django 2.2.4 on 2020-10-19 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0128_instructortouniversities'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenges',
            name='isTeamChallenge',
            field=models.BooleanField(default=False),
        ),
    ]