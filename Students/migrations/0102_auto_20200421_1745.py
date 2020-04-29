# Generated by Django 2.2.4 on 2020-04-21 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0101_auto_20200421_1658'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentgoalsetting',
            name='goalType',
        ),
        migrations.AddField(
            model_name='studentgoalsetting',
            name='goalVariable',
            field=models.IntegerField(db_index=True, default=0, verbose_name='The goal variable selected by the student. Should be a system variable index'),
        ),
        migrations.AddField(
            model_name='studentgoalsetting',
            name='targetExact',
            field=models.BooleanField(default=True, verbose_name='Indicates whether the targetedNumber should be used as a exact match or should be used as amount to gain each week'),
        ),
    ]