# Generated by Django 2.1.2 on 2021-06-10 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0117_courseconfigparams_adaptationused'),
    ]

    operations = [
        migrations.AlterField(
            model_name='courseconfigparams',
            name='adaptationUsed',
            field=models.BooleanField(default=False),
        ),
    ]