# Generated by Django 2.2.4 on 2020-01-11 22:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0087_auto_20200108_1403'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseconfigparams',
            name='betVC',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='courseconfigparams',
            name='chatUsed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='courseconfigparams',
            name='xpCalculateWarmupByMaxScore',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='leaderboardsconfig',
            name='periodicTask',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='django_celery_beat.PeriodicTask', verbose_name='the periodic task'),
        ),
        migrations.AlterField(
            model_name='virtualcurrencyperiodicrule',
            name='periodicTask',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='django_celery_beat.PeriodicTask', verbose_name='the periodic task'),
        ),
    ]
