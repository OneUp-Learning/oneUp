# Generated by Django 2.2.5 on 2019-09-20 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0083_merge_20190920_1547'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseconfigparams',
            name='contentUnlockingDisplayed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='courseconfigparams',
            name='debugSystemVariablesDisplayed',
            field=models.BooleanField(default=False),
        ),
    ]
