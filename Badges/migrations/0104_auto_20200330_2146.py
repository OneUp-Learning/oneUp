# Generated by Django 2.2.5 on 2020-03-31 01:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0103_auto_20200330_1539'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseconfigparams',
            name='hintsUsed',
            field=models.BooleanField(default=False),
        ),
    ]
