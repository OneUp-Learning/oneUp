# Generated by Django 2.2.4 on 2020-02-18 02:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0094_auto_20200213_1843'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseconfigparams',
            name='displayAchievementPage',
            field=models.BooleanField(default=True),
        ),
    ]