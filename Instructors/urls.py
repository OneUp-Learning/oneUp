from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView

from Instructors.views.activityAssignPointsView import assignedPointsList, activityAssignPointsView
from Instructors.views.activityCreateView import activityCreateView
from Instructors.views.activityListView import activityList
from Instructors.views.announcementCreateView import announcementCreateView
from Instructors.views.announcementListView import announcementList
from Instructors.views.allAnnouncementsView import allAnnouncements
 
from Instructors.views.challengeAddQuestionsView import challengeAddQuestionsView
from Instructors.views.challengeCreateView import challengeCreateView
from Instructors.views.challengeEditQuestionsView import challengeEditQuestionsView
#from Instructors.views.challengeEditView import challengeEditView
from Instructors.views.challengeListView import ChallengesList
from Instructors.views.challengeQuestionSelectView import challengeQuestionSelectView
from Instructors.views.challengeSaveSelectedQuestionsView import challengeSaveSelectedQuestions
from Instructors.views.challengeSaveView import challengeSaveView

from Instructors.views.classAchievementsView import classAchievements
from Instructors.views.classAchievementsVizView import classAchievementsViz
from Instructors.views.createStudentListView import createStudentListView
from Instructors.views.createStudentView import createStudentViewUnchecked
from Instructors.views.classSeriousAchievementsVizView import classSeriousAchievementsViz
from Instructors.views.classWarmupAchievementsVizView import classWarmupAchievementsViz

from Instructors.views.classSkillsVizView import classSkillsViz
from Instructors.views.courseInfoView import courseInformation
from Instructors.views.createStudentListView import createStudentListView
from Instructors.views.createStudentView import createStudentViewUnchecked

from Instructors.views.deleteView import deleteQuestion, deleteChallenge, deleteSkill, deleteQuestionFromChallenge, deleteUser, deleteTopic, deleteSubTopic, deleteActivity, deleteAnnouncement, deleteMilestone
from Instructors.views.essayView import  essayForm
#from Instructors.views.filesListView import  filesList
from Instructors.views.gameRulesView import gameRulesView

from Instructors.views.imageView import imageUpload, imageDelete, imageList
from Instructors.views.importStudentsView import importStudents

from Instructors.views.instructorCourseHomeView import instructorCourseHome
from Instructors.views.instructorHomeView import instructorHome
#from Instructors.views.instructorQuestionsView import InstructorQuestions

from Instructors.views.matchingView import matchingForm
from Instructors.views.milestoneCreateView import milestoneCreateView
from Instructors.views.milestoneListView import milestoneList
from Instructors.views.multipleAnswersView import multipleAnswersForm
from Instructors.views.multipleChoiceView import multipleChoiceForm
from Instructors.views.preferencesView import preferencesView

#from Instructors.views.questionListView import questionListView
from Instructors.views.searchQuestionsView import searchQuestions
from Instructors.views.searchResultsView import searchResults
from Instructors.views.skillsCreateView import skillsCreateView
from Instructors.views.skillsListView import skillsListView
from Instructors.views.studentAchievementsView import studentAchievements
from Instructors.views.studentChallengesCompletedView import studentChallengesCompleted
from Instructors.views.studentGradedChallengeView import studentGradedChallenge
from Instructors.views.studentSkillsEarnedView import studentSkillsEarned
from Instructors.views.studentTopicsView import studentTopics
from Instructors.views.subTopicsCreateView import subTopicsCreateView
from Instructors.views.subTopicsListView import subTopicsListView

from Instructors.views.topicsCreateView import topicsCreateView
from Instructors.views.topicsListView import topicsListView
from Instructors.views.trueFalseView import trueFalseNewForm
from Instructors.views.views import index

#Dynamic Questions Stuff
from Instructors.views.dynamicQuestionView import dynamicQuestionForm
from Instructors.views.templateDynamicQuestionsView import templateDynamicQuestionForm
from Instructors.views.dynamicQuestionView import dynamicQuestionPartAJAX
from Instructors.views.luaTestView import luaTestView
from Instructors.views.luaLibUploadView import luaLibUpload, libDelete, libEdit


admin.autodiscover()

urlpatterns = [
    
    url(r'^activityAssignPointsForm', assignedPointsList, name='activityAssignPointsForm'),
    url(r'^activityAssignPoints', activityAssignPointsView, name='activityAssignPoints'),
    url(r'^activitiesList',activityList, name='activityList'),
    url(r'^announcementCreate', announcementCreateView, name='announcementCreateView'),
    url(r'^announcementList', announcementList, name='announcementListView'),           
    url(r'^challengeAddQuestions',challengeAddQuestionsView, name='challengeAddQuestionsView'),
    url(r'^announcements', allAnnouncements, name='allAnnouncements'),           
    url(r'^announcementList', announcementList, name='announcementListView'),           

    url(r'^challengeCreate',challengeCreateView, name='challengeCreateView'),
    url(r'^challengeQuestionsList',challengeEditQuestionsView, name='challengeEditQuestionsView'),
#    url(r'^challengeEdit',challengeEditView, name='challengeEditView'),
    url(r'^challengesList',ChallengesList, name='ChallengesList'),
    url(r'^challengeSaveSelectedQuestions',challengeSaveSelectedQuestions, name='challengeSaveSelectedQuestions'),
    url(r'^challengeSave',challengeSaveView, name='challengeSaveView'),
    url(r'^challengeQuestionSelect',challengeQuestionSelectView, name='ChallengesList'),

    url(r'^classAchievementsViz',classAchievementsViz, name='classAchievementsViz'),
    url(r'^classSeriousAchievementsViz',classSeriousAchievementsViz, name='classSeriousAchievementsViz'),
    url(r'^classWarmupAchievementsViz',classWarmupAchievementsViz, name='classWarmupAchievementsViz'),
    url(r'^classAchievements',classAchievements, name='classAchievements'),
    url(r'^createActivity',activityCreateView,name='activityCreateView'),
    url(r'^classSkillsViz',classSkillsViz,name='classSkillsViz'),
    url(r'^courseInformation',courseInformation,name='courseInformation'),
    url(r'^createMilestone',milestoneCreateView,name='milestoneCreateView'),
    #url(r'^saveCourseInformation',saveCourseInformation,name='saveCourseInformation'),
    url(r'^createMilestone',milestoneCreateView,name='milestoneCreateView'),
    url(r'^createStudentList',createStudentListView,name='createStudentListView'),
    url(r'^createStudent',createStudentViewUnchecked,name='createStudentView'),
    url(r'^deleteActivity',deleteActivity, name='deleteActivity'),
    url(r'^deleteAnnouncement',deleteAnnouncement, name='deleteAnnouncement'),
    url(r'^deleteChallenge',deleteChallenge, name='deleteChallenge'),
    url(r'^deleteMilestone',deleteMilestone, name='deleteMilestone'),
    url(r'^deleteQuestionFromChallenge',deleteQuestionFromChallenge, name='deleteQuestionFromChallenge'),
    url(r'^deleteQuestion',deleteQuestion, name='deleteQuestion'),
    url(r'^deleteSkill',deleteSkill, name='deleteSkill'),
    url(r'^deleteTopic',deleteTopic, name='deleteTopic'),
    url(r'^deleteSubTopic',deleteSubTopic, name='deleteSubTopic'),
    url(r'^deleteUser',deleteUser, name='deleteUser'),
    url(r'^gameRules',gameRulesView,name='gameRulesView'),
    url(r'^$', index, name='home'),    
    url(r'^forms/EssayForm', essayForm, name='newEssayForm'),
    url(r'^forms/MatchingForm',matchingForm, name='newEssayForm'),
    url(r'^forms/MultipleAnswersForm', multipleAnswersForm, name='multipleAnswersForm'),
    url(r'^forms/MultipleChoiceForm', multipleChoiceForm, name='multipleChoiceForm'),
    url(r'^forms/TrueFalseForm', trueFalseNewForm, name='newTrueFalseForm'),
    url(r'^forms/DynamicQuestionForm',dynamicQuestionForm, name='Dynamic QuestionForm'),
    url(r'^forms/TemplateDynamicQuestionForm',templateDynamicQuestionForm, name='Template Dynamic QuestionForm'),
    url(r'^imageDelete',imageDelete,name='imageDelete'),
    url(r'^imageList', imageList, name='imageList'),
    url(r'^imageUpload',imageUpload,name='imageUpload'),
    url(r'^importStudents',importStudents,name='importStudents'),
    url(r'^instructorCourseHome',instructorCourseHome,name='instructorCourseHome'),
    url(r'^instructorHome',instructorHome,name='instructorHome'), 
    url(r'^milestonesList',milestoneList, name='milestoneList'),    
    url(r'^preferences',preferencesView, name='preferencesView'),
    url(r'^search',searchQuestions, name='searchQuestions'),
    url(r'^skillsCreate',skillsCreateView, name='skillsCreateView'),
    url(r'^skillsList',skillsListView, name='skillsListView'),
    url(r'^sresults',searchResults, name='searchResults'), 
    url(r'^studentAchievements',studentAchievements, name='studentAchievements'),
    url(r'^studentChallengesCompleted',studentChallengesCompleted, name='studentChallengesCompleted'),
    url(r'^studentGradedChallenge',studentGradedChallenge, name='studentGradedChallenge'),
    url(r'^studentSkillsEarned',studentSkillsEarned, name='studentSkillsEarned'),
    url(r'^studentTopics',studentTopics, name='studentTopics'),
    url(r'^subTopicsCreate',subTopicsCreateView, name='subTopicsCreateView'),
    url(r'^subTopicsListView',subTopicsListView, name='subTopicsListView'),
    url(r'^topicsCreate',topicsCreateView, name='topicsCreateView'),
    url(r'^topicsList',topicsListView, name='topicsListView'),
    url(r'^forms/doDynamicQuestion',dynamicQuestionPartAJAX,name="dynamic question engine AJAX"),
    url(r'^luaTestView',luaTestView,name="Lua Test View"),
    url(r'^luaLibDelete',libDelete,name="Lua Library Delete"), 
    url(r'^luaLibEdit',libEdit,name="Lua Library Edit"),        
    url(r'^luaLibUploadView',luaLibUpload,name="Lua Library Upload"),
   
 

   


]
