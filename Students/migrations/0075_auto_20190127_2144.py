# Generated by Django 2.0.8 on 2019-01-28 02:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0074_auto_20190126_1222'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentstreaks',
            name='streakStartDate',
            field=models.DateTimeField(blank=True, null=True, verbose_name='The date the streak reset on'),
        ),
    ]
