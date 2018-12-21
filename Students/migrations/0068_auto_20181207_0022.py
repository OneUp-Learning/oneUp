# Generated by Django 2.0.8 on 2018-12-07 05:22

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0067_duelchallenges_winners'),
    ]

    operations = [
        migrations.AddField(
            model_name='duelchallenges',
            name='acceptTime',
            field=models.DateTimeField(auto_now_add=True, db_index=True, default=django.utils.timezone.now, verbose_name='Accept Timestamp'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='duelchallenges',
            name='sendTime',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Send Timestamp'),
        ),
    ]