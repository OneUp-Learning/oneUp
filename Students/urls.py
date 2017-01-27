'''
Created on May 1, 2014

@author: iiscs
'''
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView

from Students.views.achievementsView import achievements
from Students.views.allAnnouncementsView import allAnnouncements
from Students.views.avatarView import avatar
from Students.views.challengesListView import ChallengesList
from Students.views.challengesWarmUpListView import ChallengesWarmUpList
from Students.views.challengeDescriptionView import ChallengeDescription
from Students.views.challengeSetupView import ChallengeSetup
from Students.views.challengeResultsView import ChallengeResults
from Students.views.challengesTakenView import ChallengesTaken
from Students.views.courseInfoView import CourseInformation
from Students.views.logoutView import LogoutView
from Students.views.preferencesView import preferencesView
from Students.views.selectedChallengeTakenView import SelectedChallengeTaken
from Students.views.studentCourseHomeView import StudentCourseHome
from Students.views.studentHomeView import StudentHome



admin.autodiscover()

urlpatterns = [    
    url(r'^achievements',achievements,name='achievements'),
    url(r'^avatar',avatar,name='avatar'),
    url(r'^ChallengesWarmUpList',ChallengesWarmUpList, name='ChallengesWarmUpList'),
    url(r'^ChallengesList',ChallengesList, name='ChallengesList'),
    url(r'^ChallengeDescription',ChallengeDescription, name='ChallengeDescription'),
    url(r'^Announcements', allAnnouncements, name='allAnnouncements'), 
    url(r'^ChallengeSetup',ChallengeSetup, name='ChallengeSetup'),
    url(r'^ChallengeResults',ChallengeResults, name='ChallengeResults'),
    url(r'^ChallengesTaken',ChallengesTaken, name='ChallengesTaken'),
    url(r'^CourseInformation',CourseInformation,name='CourseInformation'),
    url(r'^Preferences',preferencesView, name='preferencesView'), 
    url(r'^Logout', LogoutView, name='Logout'),       
    url(r'^SelectedChallengeTaken',SelectedChallengeTaken, name='SelectedChallengeTaken'),
    url(r'^StudentCourseHome',StudentCourseHome, name='StudentCourseHome'),
    url(r'^StudentHome',StudentHome, name='StudentHome'),


    
    # url(r'^oneUp/students/', include('Students.urls')),   
    # url(r'^blog/', include('blog.urls')),
]
