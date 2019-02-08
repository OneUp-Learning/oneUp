from django.contrib import admin

# Register your models here.
from Badges.models import ActionArguments, Conditions, Rules, Badges,BadgesInfo,PeriodicBadges, CourseConfigParams,VirtualCurrencyCustomRuleInfo,VirtualCurrencyRuleInfo, VirtualCurrencyPeriodicRule
from Badges.models import Dates, FloatConstants, StringConstants, GameMechanics, CourseMechanics, RuleEvents, LeaderboardsConfig, ProgressiveUnlocking, AttendaceStreakConfiguration


admin.site.register(ActionArguments)
admin.site.register(Conditions)
admin.site.register(Rules)
admin.site.register(Badges)
admin.site.register(BadgesInfo)
admin.site.register(PeriodicBadges)
admin.site.register(Dates)
admin.site.register(FloatConstants)
admin.site.register(StringConstants)
admin.site.register(GameMechanics)
admin.site.register(CourseConfigParams)
admin.site.register(CourseMechanics)
admin.site.register(RuleEvents)
admin.site.register(VirtualCurrencyCustomRuleInfo)
admin.site.register(VirtualCurrencyRuleInfo)
admin.site.register(VirtualCurrencyPeriodicRule)
admin.site.register(LeaderboardsConfig)
admin.site.register(ProgressiveUnlocking)
admin.site.register(AttendaceStreakConfiguration)
