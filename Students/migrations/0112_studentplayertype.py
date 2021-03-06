# Generated by Django 2.1.15 on 2021-06-05 05:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0116_playertype'),
        ('Instructors', '0132_activities_isavailable'),
        ('Students', '0111_auto_20210430_1629'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentPlayerType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Instructors.Courses', verbose_name='the related course')),
                ('playerType', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Badges.PlayerType', verbose_name='the player type')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Students.Student', verbose_name='the student')),
            ],
        ),
    ]
