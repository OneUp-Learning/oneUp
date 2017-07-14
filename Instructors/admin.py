from django.contrib import admin

# Register your models here.
from django.contrib import admin
from Instructors.models import Courses, InstructorRegisteredCourses, Tags, ResourceTags, ChallengesQuestions, CoursesSkills, QuestionsSkills, ChallengeTags,\
    TemplateDynamicQuestions, Topics, CoursesTopics
from Instructors.models import Questions, StaticQuestions, DynamicQuestions, Answers, CorrectAnswers, Challenges, MatchingAnswers, UploadedImages
from Instructors.models import Skills, Activities, Prompts, Goals, Announcements, Milestones, Instructors, TemplateTextParts, LuaLibrary, DependentLibrary,\
    QuestionLibrary
from django.template.backends.django import Template

admin.site.register(Announcements)
admin.site.register(Activities)
admin.site.register(Courses)
admin.site.register(CoursesSkills)
admin.site.register(Questions)
admin.site.register(StaticQuestions)
admin.site.register(DynamicQuestions)
admin.site.register(TemplateDynamicQuestions)
admin.site.register(QuestionsSkills)
admin.site.register(Answers)
admin.site.register(CorrectAnswers)
admin.site.register(Prompts)
admin.site.register(Goals)
admin.site.register(Challenges)
admin.site.register(Skills)
admin.site.register(MatchingAnswers)
admin.site.register(Tags)
admin.site.register(ResourceTags)
#admin.site.register(ChallengesSkills)
admin.site.register(ChallengesQuestions)
admin.site.register(ChallengeTags)
admin.site.register(Milestones)
# admin.site.register(CourseConfigParams)
admin.site.register(InstructorRegisteredCourses)
admin.site.register(UploadedImages)
admin.site.register(Instructors)
admin.site.register(TemplateTextParts)
admin.site.register(Topics)
admin.site.register(CoursesTopics)
admin.site.register(DependentLibrary)
admin.site.register(LuaLibrary)
admin.site.register(QuestionLibrary)



