# Generated by Django 2.0.8 on 2018-11-17 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0088_auto_20180817_1639'),
    ]

    operations = [
        migrations.AddField(
            model_name='activities',
            name='activityPosition',
            field=models.IntegerField(default=0),
        ),
    ]
