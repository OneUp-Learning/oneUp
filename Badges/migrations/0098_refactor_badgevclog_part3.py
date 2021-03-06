# Generated by Django 2.2.4 on 2020-02-23 20:38

from django.db import migrations, models
from Chat.serializers import UserSerializer
import json

def create_json(log, log_type):
    result = {}
    result['issuer'] = UserSerializer(log.issuer).data

    if log_type == 'Badge':
        result['student'] = UserSerializer(log.studentBadges.studentID.user).data
        result['badge'] = {'name': log.studentBadges.badgeID.badgeName, 'type': 'Manual'}

    elif log_type == 'VC':
        result['student'] = UserSerializer(log.studentVirtualCurrency.studentID.user).data
        result['vc'] = {'name': log.studentVirtualCurrency.vcRuleID.vcRuleName, 'value': log.studentVirtualCurrency.value, 'type': 'Manual'}
    
    return result

def migrate_badgesvclog(apps, schema_editor):
    BadgesVCLog = apps.get_model("Badges","BadgesVCLog")

    old_logs = BadgesVCLog.objects.all()
    for log in old_logs:
        result = {}
        if log.studentBadges:
            result = create_json(log, 'Badge')
        elif log.studentVirtualCurrency:
            result = create_json(log, 'VC')
        log.log_data = json.dumps(result)
        log.save()
        
class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0097_refactor_badgevclog_part2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='badgesvclog',
            name='issuer',
        ),
        migrations.RemoveField(
            model_name='badgesvclog',
            name='studentBadges',
        ),
        migrations.RemoveField(
            model_name='badgesvclog',
            name='studentVirtualCurrency',
        ),
    ]
