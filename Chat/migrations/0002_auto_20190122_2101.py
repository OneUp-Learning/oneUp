# Generated by Django 2.0.8 on 2019-01-23 02:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Chat', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='channel_name',
            field=models.TextField(unique=True),
        ),
    ]
