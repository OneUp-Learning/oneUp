# Generated by Django 2.1.2 on 2022-02-23 00:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0121_courseconfigparams_usecustomavatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseconfigparams',
            name='applauseOn',
            field=models.BooleanField(default=False),
        ),
    ]
