# Generated by Django 2.2.4 on 2020-02-21 22:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0093_auto_20200205_1603'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentregisteredcourses',
            name='xp',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=100),
        ),
    ]
