# Generated by Django 2.2.5 on 2020-03-30 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0102_courseconfigparams_customleaderboardsused'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseconfigparams',
            name='hintsUsed',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='courseconfigparams',
            name='weightBasicHint',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='courseconfigparams',
            name='weightStrongHint',
            field=models.IntegerField(default=0),
        ),
    ]
