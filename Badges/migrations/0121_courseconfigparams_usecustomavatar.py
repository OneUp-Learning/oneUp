# Generated by Django 2.1.2 on 2022-02-02 01:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0120_courseconfigparams_classfundenabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseconfigparams',
            name='useCustomAvatar',
            field=models.BooleanField(default=False),
        ),
    ]
