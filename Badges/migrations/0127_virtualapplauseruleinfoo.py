# Generated by Django 2.1.2 on 2022-04-21 05:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Instructors', '0140_auto_20211021_1448'),
        ('Badges', '0126_virtualapplausecustomruleinfo_applauseoption'),
    ]

    operations = [
        migrations.CreateModel(
            name='VirtualApplauseRuleInfoo',
            fields=[
                ('vaRuleID', models.AutoField(primary_key=True, serialize=False)),
                ('vaRuleName', models.CharField(max_length=300)),
                ('vaRulePosition', models.IntegerField(default=0)),
                ('ApplauseOption', models.IntegerField(default=1200)),
                ('courseID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Instructors.Courses', verbose_name='the related course')),
                ('ruleID', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Badges.Rules', verbose_name='the related rule')),
            ],
        ),
    ]