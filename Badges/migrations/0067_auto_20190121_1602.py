# Generated by Django 2.0.8 on 2019-01-21 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0066_courseconfigparams_classmateschallenges'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseconfigparams',
            name='vcCallout',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='courseconfigparams',
            name='vcDuel',
            field=models.IntegerField(default=0),
        ),
    ]
