# Generated by Django 2.1.2 on 2019-06-18 18:56

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0086_studentgoalsetting_recurringgoal'),
    ]

    operations = [
        migrations.AlterField(
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
