# Generated by Django 2.1.2 on 2021-09-26 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0119_auto_20210701_1758'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseconfigparams',
            name='classFundEnabled',
            field=models.BooleanField(default=False),
        ),
    ]
