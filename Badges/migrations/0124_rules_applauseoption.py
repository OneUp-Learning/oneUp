# Generated by Django 2.1.2 on 2022-03-23 23:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0123_auto_20220311_1728'),
    ]

    operations = [
        migrations.AddField(
            model_name='rules',
            name='applauseOption',
            field=models.IntegerField(default=1100),
        ),
    ]
