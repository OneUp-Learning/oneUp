# Generated by Django 2.2.4 on 2019-11-15 21:35

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0088_auto_20191115_1739'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentgoalsetting',
            name='progressToGoal',
            field=models.IntegerField(default=0, verbose_name='A percentage of the students progress towards the goal.'),
        ),
        migrations.AddField(
            model_name='studentgoalsetting',
            name='recurringGoal',
            field=models.BooleanField(default=True, verbose_name='A boolean value to indicate whether goal has recurrence.'),
        ),
        migrations.AlterField(
            model_name='studentgoalsetting',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
