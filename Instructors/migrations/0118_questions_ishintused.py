# Generated by Django 2.2.5 on 2020-04-09 23:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0117_auto_20200330_2146'),
    ]

    operations = [
        migrations.AddField(
            model_name='questions',
            name='isHintUsed',
            field=models.BooleanField(default=False),
        ),
    ]
