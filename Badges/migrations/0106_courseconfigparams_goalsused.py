# Generated by Django 2.2.4 on 2020-04-13 23:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0105_setup_default_dates'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseconfigparams',
            name='goalsUsed',
            field=models.BooleanField(default=False),
        ),
    ]
