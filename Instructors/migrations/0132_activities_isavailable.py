# Generated by Django 2.1.2 on 2021-05-28 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0131_auto_20210430_1629'),
    ]

    operations = [
        migrations.AddField(
            model_name='activities',
            name='isAvailable',
            field=models.BooleanField(default=True, verbose_name='Activity is available for students to see.'),
        ),
    ]