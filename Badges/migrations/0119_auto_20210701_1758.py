# Generated by Django 2.1.2 on 2021-07-01 21:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0118_auto_20210610_1112'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseconfigparams',
            name='xpDisplayUsed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='courseconfigparams',
            name='xpLeaderboardUsed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='playertype',
            name='xpDisplayUsed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='playertype',
            name='xpLeaderboardUsed',
            field=models.BooleanField(default=False),
        ),
    ]
