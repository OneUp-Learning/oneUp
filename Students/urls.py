'''
Created on May 1, 2014

@author: iiscs
'''
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import RedirectView

from Instructors.views.dynamicQuestionView import dynamicQuestionPartAJAX
from Students.views.achievementsView import (Track_class_avg_button_clicks,
                                             achievements)
from Students.views.activitesView import ActivityList
from Students.views.activityDescription import ActivityDetail
from Students.views.allAnnouncementsView import allAnnouncements
from Students.views.avatarUploadView import avatarUpload
from Students.views.avatarView import avatar
from Students.views.calloutsView import (
    callout_create, callout_description,
    get_class_callout_qualified_challenges,
    get_individual_callout_qualified_challenges)
from Students.views.challengeDescriptionView import ChallengeDescription
from Students.views.challengeResultsView import ChallengeResults
from Students.views.challengeSetupView import ChallengeSetup
from Students.views.challengesListView import ChallengesList
from Students.views.challengesTakenView import ChallengesTaken
from Students.views.challengesWarmUpListView import ChallengesWarmUpList
from Students.views.courseInfoView import CourseInformation
from Students.views.coursePerformanceView import CoursePerformance
from Students.views.duelChallengeView import (
    callouts_list, duel_challenge_accept, duel_challenge_create,
    duel_challenge_delete, duel_challenge_description,
    get_create_duel_topics_difficulties, validate_duel_challenge_creation)
from Students.views.goalsListView import goals_list
from Students.views.goalView import goal_view
from Students.views.hintsView import hintsUsed
from Students.views.leaderboardInfoView import leaderboardInfoView
from Students.views.leaderboardView import LeaderboardView
from Students.views.logoutView import LogoutView
from Students.views.preferencesView import preferencesView
from Students.views.resetPasswordView import (resetPasswordView,
                                              validateResetPassword)
from Students.views.studentCourseHomeView import (StudentCourseHome,
                                                  progressBarData)
from Students.views.studentEarnedTransactions import earnedTransactionsView
from Students.views.studentHomeView import StudentHome
from Students.views.studentNotifications import (studentNotifications,
                                                 updateNotificationTable)
from Students.views.studentQA import studentQA
from Students.views.switchToInstructorView import switchToInstructorView
from Students.views.transactionNotesView import transactionNotesView
from Students.views.transactionsView import (filterTransactions,
                                             save_transaction_reason,
                                             transactionsView)
from Students.views.virtualCurrencyRuleView import VirtualCurrencyDisplay
from Students.views.virtualCurrencyShopView import virtualCurrencyShopView

admin.autodiscover()

urlpatterns = [
    url(r'^NotificationPageUpdate', updateNotificationTable,
        name='studentNotificationsUpdate'),
    url(r'^NotificationPage', studentNotifications, name='studentNotifications'),
    url(r'^achievements', achievements, name='achievements'),
    url(r'^ActivityDescription', ActivityDetail, name='ActivityDescription'),
    url(r'^ActivityList', ActivityList, name='ActivityList'),
    url(r'^avatarUpload', avatarUpload, name='avatarUpload'),
    url(r'^avatar', avatar, name='avatar'),
    url(r'^ChallengesWarmUpList', ChallengesWarmUpList,
        name='ChallengesWarmUpList'),
    url(r'^ChallengesList', ChallengesList, name='ChallengesList'),
    url(r'^ChallengeDescription', ChallengeDescription,
        name='ChallengeDescription'),
    url(r'^Announcements', allAnnouncements, name='allAnnouncements'),
    url(r'^ChallengeSetup', ChallengeSetup, name='ChallengeSetup'),
    url(r'^ChallengeResults', ChallengeResults, name='ChallengeResults'),
    url(r'^hintsUsed', hintsUsed, name='hintsUsed'),
    url(r'^ChallengesTaken', ChallengesTaken, name='ChallengesTaken'),
    url(r'^CourseInformation', CourseInformation, name='CourseInformation'),
    url(r'^CoursePerformance', CoursePerformance, name='CoursePerformance'),
    url(r'^Preferences', preferencesView, name='preferencesView'),
    url(r'^Logout', LogoutView, name='Logout'),
    url(r'^ResetPassword', resetPasswordView, name='ResetPassword'),
    url(r'^StudentCourseHome', StudentCourseHome, name='StudentCourseHome'),
    url(r'^progressBarData', progressBarData, name='progressBarData'),
    url(r'^StudentHome', StudentHome, name='StudentHome'),
    url(r'^Transactions', transactionsView, name='Transactions'),
    url(r'^TransactionNotes', transactionNotesView, name='Transaction Notes'),
    url(r'^filterTransactions', filterTransactions, name="Filter Transactions"),
    url(r'^VirtualCurrencyRules', VirtualCurrencyDisplay,
        name='Virtual Currency Rule List'),
    url(r'^VirtualCurrencyShop', virtualCurrencyShopView,
        name='Virtual Current Shop'),
    url(r'^EarnedVCTransactions', earnedTransactionsView,
        name='Earned Virtual Currency Transactions'),
    url(r'^StudentQA', studentQA, name='Student QA'),
    url(r'^LeaderboardInfo', leaderboardInfoView, name='LeaderboardInfo'),
    url(r'^Leaderboard', LeaderboardView, name='Leaderboard'),
    url(r'^switchView', switchToInstructorView, name="switchToInstructorView"),
    url(r'^Callouts', callouts_list, name='Callouts'),
    url(r'^DuelChallengeCreate', duel_challenge_create, name='DuelChallengeCreate'),
    url(r'^DuelChallengeAccept', duel_challenge_accept, name='DuelChallengeAccept'),
    url(r'^DuelChallengeDescription', duel_challenge_description,
        name='DuelChallengeDescription'),
    url(r'^DuelChallengeDelete', duel_challenge_delete, name='DuelChallengeDelete'),
    url(r'^ValidateDuelChallengeCreate', validate_duel_challenge_creation,
        name='ValidateDuelChallengeCreate'),
    url(r'^GetCreateDuelTopicsDifficulty', get_create_duel_topics_difficulties,
        name='GetCreateDuelTopicsDifficulty'),
    url(r'^CalloutCreate', callout_create, name="CalloutCreate"),
    url(r'ClassCalloutQualifiedChallenges', get_class_callout_qualified_challenges,
        name="ClassCalloutQualifiedChallenges"),
    url(r'IndividualCalloutQualifiedChallenges', get_individual_callout_qualified_challenges,
        name='IndividualCalloutQualifiedChallenges'),
    url(r'CalloutDescription', callout_description, name="CalloutDescription"),
    url(r'^ValidateResetPassword', validateResetPassword,
        name='ValidateResetPassword'),
    url(r'^Track_class_avg_button_clicks', Track_class_avg_button_clicks,
        name='Track_class_avg_button_clicks'),
    url(r'^doDynamicQuestion', dynamicQuestionPartAJAX,
        name="dynamic question engine AJAX"),
    url(r'SaveTransactionReason', save_transaction_reason,
        name="Save Transaction Reason"),
    url(r'^goalslist',goals_list, name='goalslist'),
    url(r'^goal', goal_view, name='goal'),

]
