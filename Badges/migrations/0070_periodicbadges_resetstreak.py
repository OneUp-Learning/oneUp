# Generated by Django 2.0.8 on 2019-01-25 00:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0069_auto_20190123_2312'),
    ]

    operations = [
        migrations.AddField(
            model_name='periodicbadges',
            name='resetStreak',
            field=models.BooleanField(default=False),
        ),
    ]
