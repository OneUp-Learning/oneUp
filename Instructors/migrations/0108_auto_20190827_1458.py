# Generated by Django 2.1.2 on 2019-08-27 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0107_auto_20190610_0103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='announcements',
            name='subject',
            field=models.CharField(default='', max_length=100),
        ),
    ]
