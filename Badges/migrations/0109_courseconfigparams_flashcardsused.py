# Generated by Django 2.2.4 on 2020-07-09 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0108_auto_20200708_1326'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseconfigparams',
            name='flashcardsUsed',
            field=models.BooleanField(default=True),
        ),
    ]