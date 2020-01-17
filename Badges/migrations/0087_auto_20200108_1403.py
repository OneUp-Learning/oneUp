# Generated by Django 2.1.2 on 2020-01-08 19:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0086_celerytasklog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='periodicbadges',
            name='periodicTask',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='django_celery_beat.PeriodicTask', verbose_name='the periodic task'),
        ),
    ]