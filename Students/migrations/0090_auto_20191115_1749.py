# Generated by Django 2.2.4 on 2019-11-15 22:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Students', '0089_auto_20191115_1635'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentactions',
            name='callouts_accepted',
        ),
        migrations.RemoveField(
            model_name='studentactions',
            name='callouts_sent',
        ),
        migrations.RemoveField(
            model_name='studentactions',
            name='duels_accepted',
        ),
        migrations.RemoveField(
            model_name='studentactions',
            name='duels_sent',
        ),
        migrations.RemoveField(
            model_name='studentactions',
            name='serious_attempted',
        ),
        migrations.RemoveField(
            model_name='studentactions',
            name='warmups_attempted',
        ),
        migrations.CreateModel(
            name='StudentActionsLoop',
            fields=[
                ('studentActionsLoopID', models.AutoField(primary_key=True, serialize=False)),
                ('warmups_attempted', models.IntegerField(default=0, verbose_name='# of Warmups Attempted')),
                ('serious_attempted', models.IntegerField(default=0, verbose_name='# of Serious Challenges Attempted')),
                ('duels_sent', models.IntegerField(default=0, verbose_name='# of Duels Sent')),
                ('duels_accepted', models.IntegerField(default=0, verbose_name='# of Duels Accepted')),
                ('callouts_sent', models.IntegerField(default=0, verbose_name='# of Callouts Accpeted')),
                ('callouts_participated', models.IntegerField(default=0, verbose_name='# of Callouts Participated')),
                ('high_score_challenges', models.IntegerField(default=0, verbose_name='# of High Score Challenges')),
                ('vc_earned', models.IntegerField(default=0, verbose_name='# of VC Earned')),
                ('badges_earned', models.IntegerField(default=0, verbose_name='# of Badges Earned')),
                ('on_leaderboard', models.BooleanField(default=False, verbose_name='Appeared on Leaderboard')),
                ('duels_won', models.IntegerField(default=0, verbose_name='# of Duels Won')),
                ('callouts_won', models.IntegerField(default=0, verbose_name='# of Callouts Won')),
                ('low_score_challenges', models.IntegerField(default=0, verbose_name='# of Low Score Challenges')),
                ('duels_lost', models.IntegerField(default=0, verbose_name='# of Duels Lost')),
                ('callouts_lost', models.IntegerField(default=0, verbose_name='# of Callouts Lost')),
                ('timestamp', models.DateTimeField(auto_now=True, verbose_name='Created Timestamp')),
                ('studentActionsID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Students.StudentActions', verbose_name='the overall loop')),
            ],
        ),
    ]