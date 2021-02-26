from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView

from Instructors.views.activityAssignPointsView import (
    activityAssignPointsView, assignedPointsList)
from Instructors.views.activityCategories import (activityCatCreate,
                                                  activityCatDelete,
                                                  activityCatList)
from Instructors.views.activityCreateView import (activityCreateView,
                                                  removeFileFromActivty)
from Instructors.views.activityListView import activityList, reorderActivities
from Instructors.views.activityScoreView import activityScore
from Instructors.views.addExistingStudentView import (addExistingStudent,
                                                      addStudentListView)
from Instructors.views.announcementCreateView import announcementCreateView
from Instructors.views.announcementListView import announcementList
from Instructors.views.attendanceStreaks import attendanceStreaks
from Instructors.views.CalloutReportView import (callout_challenge_report,
                                                 callout_report)
from Instructors.views.challengeAddQuestionsView import \
    challengeAddQuestionsView
from Instructors.views.challengeAdjusmentView import (adjustmentList,
                                                      challengeAdjustmentView)
from Instructors.views.challengeCreateView import challengeCreateView

from Instructors.views.challengeListView import (challengesList,
                                                 warmUpChallengeList)
from Instructors.views.challengeQuestionsListView import (
    challengeQuestionsListView, deleteProblemsButFilterTakenByStudent)
from Instructors.views.challengeSaveSelectedQuestionsView import \
    challengeSaveSelectedQuestions
from Instructors.views.classAchievementsView import classAchievements
from Instructors.views.classAchievementsVizView import classAchievementsViz
from Instructors.views.courseConfiguration import courseConfigurationView
from Instructors.views.courseImportExportView import (exportCourse,
                                                      importCourse,
                                                      validateCourseExport)
from Instructors.views.challengeExportImportView import (exportChallenge,
                                                      importChallenge,
                                                      validateChallengeExport)
from Instructors.views.courseInfoView import courseInformation
from Instructors.views.createStudentListView import createStudentListView
from Instructors.views.createStudentView import createStudentViewUnchecked, validateCreateStudent

from Instructors.views.deleteView import deleteQuestion, deleteChallenge, deleteSkill, deleteQuestionFromChallenge, deleteUser, deleteStudent, deleteTopic, deleteActivity, deleteAnnouncement, deleteManualSpendRule
from Instructors.views.imageView import imageUpload, imageDelete, imageList
from Instructors.views.importStudentsView import importStudents, saveImportStudentsPasswords

from Instructors.views.createStudentView import (createStudentViewUnchecked,
                                                 validateCreateStudent)
from Instructors.views.debugStudentEventLog import debugEventVars
from Instructors.views.debugSysVars import debugSysVars, getObjsForSysVar
from Instructors.views.deleteView import (deleteActivity, deleteAnnouncement,
                                          deleteChallenge,
                                          deleteManualSpendRule,
                                          deleteQuestion,
                                          deleteQuestionFromChallenge,
                                          deleteSkill, deleteStudent,
                                          deleteTopic, deleteUser, deleteFlashCard, deleteGroup)
from Instructors.views.DuelReportView import duel_challenge_report, duel_report
from Instructors.views.dynamicLeaderboardView import dynamicLeaderboardView
# Dynamic Questions Stuff
from Instructors.views.dynamicQuestionView import (dynamicQuestionForm,
                                                   dynamicQuestionPartAJAX)
from Instructors.views.exportGradeBookView import exportGradebook
from Instructors.views.imageView import imageDelete, imageList, imageUpload
from Instructors.views.importStudentsView import (importStudents,
                                                  saveImportStudentsPasswords)
from Instructors.views.instructorCourseHomeView import instructorCourseHome
from Instructors.views.instructorHomeView import instructorHome
from Instructors.views.instructorNotifications import (
    instructorNotifications, updateNotificationTable)
from Instructors.views.instructorQA import instructorQA
from Instructors.views.leaderboardView import LeaderboardInstructorsView
from Instructors.views.luaLibUploadView import (libDelete,
                                                libDeleteConfirmView, libEdit,
                                                luaLibUpload)
from Instructors.views.luaTestView import luaTestView
from Instructors.views.matchingView import matchingForm
from Instructors.views.multipleAnswersView import multipleAnswersForm
from Instructors.views.multipleChoiceView import multipleChoiceForm
from Instructors.views.parsonsView import parsonsForm
from Instructors.views.preferencesView import preferencesView
from Instructors.views.reorderChallengeSaveQuestions import \
    reorderChallengeSaveQuestions
from Instructors.views.reorderChallengesView import reorderChallenges
from Instructors.views.reorderViews import (receive_item_in_section,
                                            reorder_list)
from Instructors.views.resetTestStudentData import resetTestStudent
from Instructors.views.searchQuestionsView import searchQuestions
from Instructors.views.searchResultsView import searchResults
from Instructors.views.skillsCreateView import skillsCreateView
from Instructors.views.skillsListView import skillsListView
from Instructors.views.studentAchievementsView import studentAchievements
from Instructors.views.studentAttendanceReportView import \
    studentAttendanceReportView
from Instructors.views.studentAttendanceView import studentAttendance
from Instructors.views.studentSkillsEarnedView import studentSkillsEarned
from Instructors.views.studentSummaryView import studentSummary
from Instructors.views.switchToStudentView import switchToStudentView
from Instructors.views.templateDynamicQuestionsView import (
    removeFileFromQuestion, templateDynamicQuestionForm)
from Instructors.views.topicsCreateView import topicsCreateView
from Instructors.views.topicsListView import topicsListView
from Instructors.views.trueFalseView import trueFalseNewForm
from Instructors.views.views import index
from Instructors.views.whoAddedVCAndBadgeView import whoAddedBadgeAndVC

# Dynamic Questions Stuff
from Instructors.views.dynamicQuestionView import dynamicQuestionForm
from Instructors.views.templateDynamicQuestionsView import templateDynamicQuestionForm, removeFileFromQuestion
from Instructors.views.dynamicQuestionView import dynamicQuestionPartAJAX
from Instructors.views.luaTestView import luaTestView
from Instructors.views.luaLibUploadView import luaLibUpload, libDelete, libEdit, libDeleteConfirmView
from Instructors.views.studentAttendanceView import studentAttendance
from Instructors.views.studentAttendanceReportView import studentAttendanceReportView

from Instructors.views.switchToStudentView import switchToStudentView
from Instructors.views.resetTestStudentData import resetTestStudent

from Instructors.views.dynamicLeaderboardView import dynamicLeaderboardView

from Instructors.views.addExistingStudentView import addStudentListView, addExistingStudent
from Instructors.views.activityListView import reorderActivities
from Instructors.views.attendanceStreaks import attendanceStreaks

from Instructors.views.DuelReportView import duel_report, duel_challenge_report
from Instructors.views.CalloutReportView import callout_report, callout_challenge_report

from Instructors.views.leaderboardView import LeaderboardInstructorsView

#FlashCards
from Instructors.views.flashCardGroupListView import groupListView, validateFlashCard
from Instructors.views.flashCardGroupCreateView import groupCreateView
from Instructors.views.flashCardCreateView import CreateFlashCards

from Instructors.views.reorderViews import reorderGroups
admin.autodiscover()
urlpatterns = [

    url(r'^activityRemoveFile', removeFileFromActivty,
        name='removeFileFromActivty'),
    url(r'^remQuestionFileTempQ', removeFileFromQuestion,
        name="removeFileFromQuestion"),
    url(r'^activityAssignPointsForm', assignedPointsList,
        name='activityAssignPointsForm'),
    url(r'^activityAssignPoints', activityAssignPointsView,
        name='activityAssignPoints'),
    url(r'^activityCatsCreate', activityCatCreate,
        name='activityCategoriesCreateForm'),
    url(r'^activityCatsDelete', activityCatDelete,
        name='activityCategoriesDeleteForm'),
    url(r'^activityCats', activityCatList, name='activityCategories'),
    url(r'^activitiesList', activityList, name='activityList'),
    url(r'^announcementCreate', announcementCreateView,
        name='announcementCreateView'),
    url(r'^announcementList', announcementList, name='announcementListView'),
    url(r'^challengeAddQuestions', challengeAddQuestionsView,
        name='challengeAddQuestionsView'),
    url(r'^announcementList', announcementList, name='announcementListView'),
    url(r'^challengeCreate', challengeCreateView, name='challengeCreateView'),
    url(r'^challengeQuestionsList', challengeQuestionsListView,
        name='challengeQuestionsListView'),
    url(r'^challengesList', challengesList, name='ChallengesList'),
    url(r'^challengeSaveSelectedQuestions', challengeSaveSelectedQuestions,
        name='challengeSaveSelectedQuestions'),
    url(r'^classAchievementsViz', classAchievementsViz,
        name='classAchievementsViz'),
    url(r'^classAchievements', classAchievements, name='classAchievements'),
    url(r'^createActivity', activityCreateView, name='activityCreateView'),
    url(r'^exportCourse', exportCourse, name='exportCourse'),
    url(r'^validateCourseExport', validateCourseExport,
        name='validateCourseExport'),
    url(r'^importCourse', importCourse, name='importCourse'),
    url(r'^exportChallenge', exportChallenge, name='exportChallenge'),
    url(r'^validateChallengeExport', validateChallengeExport,
        name='validateChallengeExport'),
    url(r'^importChallenge', importChallenge, name='importChallenge'),
    url(r'^courseInformation', courseInformation, name='courseInformation'),
    url(r'^createStudentList', createStudentListView,
        name='createStudentListView'),
    url(r'^createStudent', createStudentViewUnchecked, name='createStudentView'),
    url(r'^courseConfiguration', courseConfigurationView,
        name='courseConfigurationView'),
    url(r'^debugEventLog', debugEventVars, name='debugSystemVar'),
    url(r'^debugSysVar', debugSysVars, name='debugSysVars'),
    url(r'^getObjsForSysVar', getObjsForSysVar, name='getObjsForSysVar'),
    url(r'^deleteActivity', deleteActivity, name='deleteActivity'),
    url(r'^deleteAnnouncement', deleteAnnouncement, name='deleteAnnouncement'),
    url(r'^deleteChallenge', deleteChallenge, name='deleteChallenge'),
    url(r'^deleteProblemsButFilterTakenByStudent', deleteProblemsButFilterTakenByStudent, name='deleteProblemsButFilterTakenByStudent'),
    url(r'^deleteQuestionFromChallenge', deleteQuestionFromChallenge,
        name='deleteQuestionFromChallenge'),
    url(r'^deleteQuestion', deleteQuestion, name='deleteQuestion'),
    url(r'^deleteSkill', deleteSkill, name='deleteSkill'),
    url(r'^deleteManualSpendRule', deleteManualSpendRule,
        name='deleteManualSpendRule'),
    url(r'^deleteTopic', deleteTopic, name='deleteTopic'),
    url(r'^deleteStudent', deleteStudent, name='deleteStudent'),
    url(r'^deleteGroup', deleteGroup, name='deleteGroup'),
    url(r'^deleteFlashCard', deleteFlashCard, name='deleteFlashCard'),
    #    url(r'^deleteUser', deleteUser, name='deleteUser'),
    url(r'^$', index, name='home'),
   
    url(r'^forms/MatchingForm', matchingForm, name='newEssayForm'),
    url(r'^forms/MultipleAnswersForm',
        multipleAnswersForm, name='multipleAnswersForm'),
    url(r'^forms/MultipleChoiceForm',
        multipleChoiceForm, name='multipleChoiceForm'),
    url(r'^forms/ParsonsForm', parsonsForm, name='parsonsForm'),
    url(r'^forms/TrueFalseForm', trueFalseNewForm, name='newTrueFalseForm'),
    url(r'^forms/DynamicQuestionForm',
        dynamicQuestionForm, name='Dynamic QuestionForm'),
    url(r'^forms/TemplateDynamicQuestionForm',
        templateDynamicQuestionForm, name='Template Dynamic QuestionForm'),
    url(r'^imageDelete', imageDelete, name='imageDelete'),
    url(r'^imageList', imageList, name='imageList'),
    url(r'^imageUpload', imageUpload, name='imageUpload'),
  
    url(r'^importStudents', importStudents, name='importStudents'),
    url(r'^saveImportStudentsPasswords', saveImportStudentsPasswords,
        name='saveImportStudentsPasswords'),
    url(r'^instructorCourseHome', instructorCourseHome,
        name='instructorCourseHome'),
    url(r'^instructorHome', instructorHome, name='instructorHome'),
    url(r'^instructorQA', instructorQA, name='instructorQA'),
    url(r'^NotificationPage', instructorNotifications,
        name='instructorNotifications'),
    url(r'^NotificationPageUpdate', updateNotificationTable,
        name='instructorNotificationUpdate'),
    url(r'^preferences', preferencesView, name='preferencesView'),
    url(r'^reorderChallenges', reorderChallenges, name='reorderChallenges'),
    url(r'^reorderChallengeSaveQuestions', reorderChallengeSaveQuestions,
        name='reorderChallengeSaveQuestions'),
   
    url(r'^search', searchQuestions, name='searchQuestions'),
    url(r'^skillsCreate', skillsCreateView, name='skillsCreateView'),
    url(r'^skillsList', skillsListView, name='skillsListView'),
    url(r'^sresults', searchResults, name='searchResults'),
    url(r'^studentAchievements', studentAchievements, name='studentAchievements'),
    url(r'^studentSkillsEarned', studentSkillsEarned, name='studentSkillsEarned'),
    url(r'^studentSummary', studentSummary, name='studentSummary'),
    url(r'^topicsCreate', topicsCreateView, name='topicsCreateView'),
    url(r'^topicsList', topicsListView, name='topicsListView'),
  
    url(r'^warmUpChallengeList', warmUpChallengeList, name='warmUpChallengeList'),
    url(r'^forms/doDynamicQuestion', dynamicQuestionPartAJAX,
        name="dynamic question engine AJAX"),
    url(r'^luaTestView', luaTestView, name="Lua Test View"),
    url(r'^luaLibDelete', libDelete, name="Lua Library Delete"),
    url(r'^luaLibEdit', libEdit, name="Lua Library Edit"),
    url(r'^luaLibUploadView', luaLibUpload, name="Lua Library Upload"),
    url(r'^luaLibConfirmDelete', libDeleteConfirmView,
        name="Lua Library Deletion Confirmation"),
    url(r'^adjustmentList', adjustmentList, name='adjustmentList'),
    url(r'^challengeAdjustment', challengeAdjustmentView,
        name='challengeAdjustmentView'),
    url(r'^activityScore', activityScore, name='activityScore'),
    url(r'^exportGradebook', exportGradebook, name='exportGradebook'),
    url(r'^validateCreateStudent', validateCreateStudent,
        name='validateCreateStudentView'),
    url(r'^studentAttendanceReport', studentAttendanceReportView,
        name='studentAttendanceReportView'),
    url(r'^studentAttendance', studentAttendance, name='studentAttendance'),
    url(r'^switchView', switchToStudentView, name='swtichView'),
    url(r'^resetTestStudent', resetTestStudent, name='resetTestStudent'),
    url(r'^reorderActivities', reorderActivities, name="addExistingStudent"),
    url(r'^dynamicLeaderboard', dynamicLeaderboardView,
        name='dynamicLeaderboardView'),
    url(r'^addStudentListView', addStudentListView, name='addStudentListView'),
    url(r'^addExistingStudent', addExistingStudent, name="addExistingStudent"),
    url(r'^attendanceStreaks', attendanceStreaks, name="attendanceStreaks"),
    url(r'^DuelReport', duel_report,
        name="duel_report"),
    url(r'^DuelChallengeReport', duel_challenge_report, name="DuelChallengeReport"),
    url(r'^CalloutReport', callout_report,
        name="callout_report"),
    url(r'^CalloutChallengeReport', callout_challenge_report,
        name="CalloutChallengeReport"),
    url(r'^instructorLeaderboard', LeaderboardInstructorsView,
        name="instructorLeaderboard"),
    url(r'^whoAddedBadgeAndVC', whoAddedBadgeAndVC, name="whoAddedBadgeAndVC"),
    url(r'^reorderList', reorder_list, name="reorderList"),
    url(r'^receiveItemInSection', receive_item_in_section, name="receive_item_in_section"),
    # Flash cards
    url(r'^groupList', groupListView, name='groupListView'),
    url(r'^validateFlashCard', validateFlashCard, name='groupListView'),
    url(r'^groupCreate', groupCreateView, name='groupCreateView'),
    url(r'^createFlashCard', CreateFlashCards, name='createFlashCard'),
    url(r'^ReorderGroups', reorderGroups, name='reorderGroups')
]

