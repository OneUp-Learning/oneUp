# Generated by Django 2.0.8 on 2018-11-02 05:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0066_studentprogressiveunlocking_objecttype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentprogressiveunlocking',
            name='pUnlockingRuleID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Badges.ProgressiveUnlocking', verbose_name='the progressive unlocking rule'),
        ),
    ]
