# Generated by Django 2.0.8 on 2019-01-23 01:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_name', models.TextField(db_index=True, unique=True)),
                ('channel_url', models.SlugField(blank=True, null=True, unique=True)),
                ('topic', models.TextField(blank=True, max_length=40, null=True)),
                ('channel_course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Instructors.Courses', verbose_name='the related course')),
                ('creator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='creator', to=settings.AUTH_USER_MODEL)),
                ('users', models.ManyToManyField(blank=True, related_name='subscribers', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('timestamp', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Chat.Channel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]