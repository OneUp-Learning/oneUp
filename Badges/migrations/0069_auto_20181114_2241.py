# Generated by Django 2.0.8 on 2018-11-15 03:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0068_auto_20181107_2042'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaderboardsconfig',
            name='continousHowFarBack',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='leaderboardsconfig',
            name='timePeriodUpdateInterval',
            field=models.IntegerField(default=0),
        ),
    ]