# Generated by Django 2.2.4 on 2021-01-04 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0113_courseconfigparams_selfassignment'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseconfigparams',
            name='minimumCreditPercentage',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='courseconfigparams',
            name='activitiesUsed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='courseconfigparams',
            name='announcementsUsed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='courseconfigparams',
            name='calloutAfterWarmup',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='courseconfigparams',
            name='courseAvailable',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='courseconfigparams',
            name='displayAchievementPage',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='courseconfigparams',
            name='flashcardsUsed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='courseconfigparams',
            name='gradebookUsed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='courseconfigparams',
            name='progressBarUsed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='courseconfigparams',
            name='studCanChangeGoal',
            field=models.BooleanField(default=False),
        ),
    ]