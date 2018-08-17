# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0002_auto_20150421_1705'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='user',
            field=models.OneToOneField(default=0, to=settings.AUTH_USER_MODEL,on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
