# Generated by Django 2.0.8 on 2020-04-15 21:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0098_merge_20200410_1447'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentregisteredcourses',
            name='level',
            field=models.IntegerField(default=0),
        ),
    ]