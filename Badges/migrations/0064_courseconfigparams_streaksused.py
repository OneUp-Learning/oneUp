# Generated by Django 2.0.8 on 2019-01-01 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0063_auto_20181011_1316'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseconfigparams',
            name='streaksUsed',
            field=models.BooleanField(default=False),
        ),
    ]
