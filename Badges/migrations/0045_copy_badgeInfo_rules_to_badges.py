# -*- coding: utf-8 -*-
# Manually written
from __future__ import unicode_literals

from django.db import migrations

def copy_badges(apps,schema_editor):
    Badges = apps.get_model("Badges","Badges")
    BadgesInfo = apps.get_model("Badges","BadgesInfo")
    for badgeInfo in BadgesInfo.objects.all():
        badge = Badges(badgesinfo_ptr=badgeInfo)
        badge.courseID = badgeInfo.courseID
        badge.badgeID = badgeInfo.badgeID
        badge.badgeName = badgeInfo.badgeName
        badge.badgeDescription = badgeInfo.badgeDescription
        badge.badgeImage= badgeInfo.badgeImage
        badge.ruleID = badgeInfo.ruleID
        badge.futureRuleID = badgeInfo.ruleID
        badge.save()

class Migration(migrations.Migration):

    dependencies = [
        ('Badges', '0044_auto_20180516_1459'),
    ]

    operations = [
        migrations.RunPython(copy_badges)
    ]