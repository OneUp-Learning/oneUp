# Generated by Django 2.2.4 on 2020-12-07 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0112_auto_20201121_2126'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseconfigparams',
            name='selfAssignment',
            field=models.BooleanField(default=True, verbose_name='Students can auto-assign themselves to teams'),
        ),
    ]