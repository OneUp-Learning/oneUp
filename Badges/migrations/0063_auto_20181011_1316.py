# Generated by Django 2.0.8 on 2018-10-11 17:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0062_auto_20181011_1311'),
    ]

    operations = [
        migrations.AlterField(
            model_name='periodicbadges',
            name='periodicTask',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='django_celery_beat.PeriodicTask', verbose_name='the periodic task'),
        ),
        migrations.AlterField(
            model_name='virtualcurrencyperiodicrule',
            name='periodicTask',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='django_celery_beat.PeriodicTask', verbose_name='the periodic task'),
        ),
    ]