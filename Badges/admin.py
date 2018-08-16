from django.contrib import admin

# Register your models here.
from Badges.models import ActionArguments, Conditions, Rules, Badges,BadgesInfo, CourseConfigParams,VirtualCurrencyCustomRuleInfo,VirtualCurrencyRuleInfo
from Badges.models import Dates, FloatConstants, StringConstants, GameMechanics, CourseMechanics, RuleEvents


admin.site.register(ActionArguments)
admin.site.register(Conditions)
admin.site.register(Rules)
admin.site.register(Badges)
admin.site.register(BadgesInfo)
admin.site.register(Dates)
admin.site.register(FloatConstants)
admin.site.register(StringConstants)
admin.site.register(GameMechanics)
admin.site.register(CourseConfigParams)
admin.site.register(CourseMechanics)
admin.site.register(RuleEvents)
admin.site.register(VirtualCurrencyCustomRuleInfo)
admin.site.register(VirtualCurrencyRuleInfo)

