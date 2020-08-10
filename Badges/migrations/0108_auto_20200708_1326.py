# Generated by Django 2.2.4 on 2020-07-08 17:26

import Badges.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0107_auto_20200415_1646'),
    ]

    operations = [
        migrations.AlterField(
            model_name='badgesvclog',
            name='timestamp',
            field=models.DateTimeField(blank=True, default=Badges.models.custom_now),
        ),
        migrations.AlterField(
            model_name='celerytasklog',
            name='timestamp',
            field=models.DateTimeField(default=Badges.models.custom_now, help_text='The last time the celery task has run completely and was recorded', verbose_name='Task Timestamp'),
        ),
        migrations.AlterField(
            model_name='courseconfigparams',
            name='courseEndDate',
            field=models.DateField(default=Badges.models.custom_now),
        ),
        migrations.AlterField(
            model_name='courseconfigparams',
            name='courseStartDate',
            field=models.DateField(default=Badges.models.custom_now),
        ),
        migrations.AlterField(
            model_name='leaderboardsconfig',
            name='lastModified',
            field=models.DateTimeField(default=Badges.models.custom_now),
        ),
        migrations.AlterField(
            model_name='periodicbadges',
            name='lastModified',
            field=models.DateTimeField(default=Badges.models.custom_now),
        ),
        migrations.AlterField(
            model_name='virtualcurrencyperiodicrule',
            name='lastModified',
            field=models.DateTimeField(default=Badges.models.custom_now),
        ),
    ]