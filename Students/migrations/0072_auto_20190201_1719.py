# Generated by Django 2.0.8 on 2019-02-01 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0071_studentconfigparams_participateinduel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='duelchallenges',
            name='customMessage',
            field=models.CharField(default='', max_length=6000),
        ),
    ]
