# Register your models here.
from django.contrib import admin
from Instructors.models import Courses, InstructorRegisteredCourses, Tags, ResourceTags, ChallengesQuestions, CoursesSkills, QuestionsSkills, ChallengeTags,\
    TemplateDynamicQuestions, Topics, CoursesTopics, ChallengesTopics, ActivitiesCategory
from Instructors.models import Questions, StaticQuestions, DynamicQuestions, Answers, CorrectAnswers, Challenges, MatchingAnswers, UploadedImages, UploadedFiles
from Instructors.models import Skills, Activities, Prompts, Goals, Announcements, Milestones, Instructors, TemplateTextParts, LuaLibrary, DependentLibrary,\
    QuestionLibrary, UploadedFiles, UploadedActivityFiles, QuestionProgrammingFiles, FlashCardGroup, FlashCardGroupCourse, FlashCards, FlashCardToGroup
from django.template.backends.django import Template

from Instructors.models import (Activities, ActivitiesCategory, Announcements,
                                Answers, Challenges, ChallengesQuestions,
                                ChallengesTopics, ChallengeTags,
                                CorrectAnswers, Courses, CoursesSkills,
                                CoursesTopics, DependentLibrary,
                                DynamicQuestions, InstructorRegisteredCourses,
                                Instructors, LuaLibrary, MatchingAnswers,
                                Prompts, QuestionLibrary,
                                QuestionProgrammingFiles, Questions,
                                QuestionsSkills, ResourceTags, Skills,
                                StaticQuestions, Tags,
                                TemplateDynamicQuestions, TemplateTextParts,
                                Topics, UploadedActivityFiles, UploadedFiles,
                                UploadedImages)

admin.site.register(Announcements)
admin.site.register(UploadedActivityFiles)
admin.site.register(Activities)
admin.site.register(ActivitiesCategory)
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
admin.site.register(Challenges)
admin.site.register(Skills)
admin.site.register(MatchingAnswers)
admin.site.register(Tags)
admin.site.register(ResourceTags)
admin.site.register(ChallengesQuestions)
admin.site.register(ChallengeTags)
admin.site.register(ChallengesTopics)
admin.site.register(InstructorRegisteredCourses)
admin.site.register(UploadedImages)
admin.site.register(UploadedFiles)
admin.site.register(Instructors)
admin.site.register(TemplateTextParts)
admin.site.register(QuestionProgrammingFiles)
admin.site.register(Topics)
admin.site.register(CoursesTopics)
admin.site.register(DependentLibrary)
admin.site.register(LuaLibrary)
admin.site.register(QuestionLibrary)
admin.site.register(FlashCards)
admin.site.register(FlashCardGroup)
admin.site.register(FlashCardGroupCourse)
admin.site.register(FlashCardToGroup)




