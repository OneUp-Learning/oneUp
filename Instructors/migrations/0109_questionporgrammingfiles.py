# Generated by Django 2.0.8 on 2019-10-29 20:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Instructors', '0108_auto_20190827_1458'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionPorgrammingFiles',
            fields=[
                ('programmingFileID', models.AutoField(primary_key=True, serialize=False)),
                ('programmingFileName', models.CharField(max_length=200)),
                ('programmingFileFolderName', models.CharField(max_length=200)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('programmingFileUploader', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Creator')),
                ('questionID', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Instructors.Questions', verbose_name='the related question')),
            ],
        ),
    ]