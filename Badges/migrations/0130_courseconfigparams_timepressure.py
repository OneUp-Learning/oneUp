# Generated by Django 2.1.2 on 2022-05-25 00:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0129_merge_20220518_2319'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseconfigparams',
            name='timePressure',
            field=models.BooleanField(default=False),
        ),
    ]
