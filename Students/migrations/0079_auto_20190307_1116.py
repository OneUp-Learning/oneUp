# Generated by Django 2.1.2 on 2019-03-07 16:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0078_auto_20190306_1428'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentgoalsetting',
            name='objectID',
        ),
        migrations.RemoveField(
            model_name='studentgoalsetting',
            name='vcRuleID',
        ),
    ]
