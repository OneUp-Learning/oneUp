from django.contrib import admin

# Register your models here.
from Students.models import Student, StudentRegisteredCourses, StudentChallenges, StudentChallengeQuestions, StudentBadges, DuelChallenges, Winners
from Students.models import StudentChallengeAnswers, MatchShuffledAnswers, StudentCourseSkills, StudentVirtualCurrency, StudentProgressiveUnlocking
from Students.models import StudentEventLog,StudentConfigParams,StudentLeaderboardHistory, StudentActivities, StudentFile, StudentVirtualCurrencyTransactions, UploadedAvatarImage, StudentAttendance, PeriodicallyUpdatedleaderboards


admin.site.register(Student)
admin.site.register(StudentActivities)
admin.site.register(StudentChallenges)
admin.site.register(StudentBadges)
admin.site.register(StudentChallengeQuestions)
admin.site.register(StudentChallengeAnswers)
admin.site.register(MatchShuffledAnswers)
admin.site.register(StudentCourseSkills)
admin.site.register(StudentEventLog)
admin.site.register(StudentRegisteredCourses)
admin.site.register(StudentConfigParams)
admin.site.register(StudentLeaderboardHistory)
admin.site.register(StudentFile)
admin.site.register(UploadedAvatarImage)
admin.site.register(StudentVirtualCurrencyTransactions)
admin.site.register(StudentVirtualCurrency)
admin.site.register(StudentAttendance)
admin.site.register(PeriodicallyUpdatedleaderboards)
admin.site.register(DuelChallenges)
admin.site.register(Winners)
admin.site.register(StudentProgressiveUnlocking)
