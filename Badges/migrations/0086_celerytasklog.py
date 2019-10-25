# Generated by Django 2.2.4 on 2019-10-17 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0085_badgesvclog'),
    ]

    operations = [
        migrations.CreateModel(
            name='CeleryTaskLog',
            fields=[
                ('celeryTaskLogID', models.AutoField(primary_key=True, serialize=False)),
                ('taskID', models.CharField(help_text='The Unique Task ID. (Example: "unique_warmups_123_badge")', max_length=200, unique=True, verbose_name='Task ID')),
                ('parameters', models.TextField(blank=True, default='{}', help_text='JSON encoded keyword arguments of celery parameters. (Example: {"argument": "value"})', verbose_name='Task Parameters')),
                ('timestamp', models.DateTimeField(auto_now=True, help_text='The last time the celery task has run completely and was recorded', verbose_name='Task Timestamp')),
            ],
        ),
    ]
