# Generated by Django 2.1.15 on 2021-04-30 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0130_universities_universitypostfix'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activities',
            name='description',
            field=models.CharField(default='', max_length=2000),
        ),
    ]
