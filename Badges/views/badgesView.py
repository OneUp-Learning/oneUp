'''
Created on Oct 29, 2014

@author: Swapna
'''

from django.template import RequestContext
from django.shortcuts import render

from Badges.models import Badges, Courses

from django.contrib.auth.decorators import login_required
from Students.views.utils import studentInitialContextDict
from Badges.models import CourseConfigParams
from Students.models import StudentConfigParams


@login_required
def BadgesMain(request):
 
    context_dict = { }
    
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
    
    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected'
        
    badgeId = [] 
    badgeName = []
    badgeImage = []
    badgeDescription = []
    #Displaying the list of challenges from database
    badges = Badges.objects.filter(courseID=currentCourse)
    for badge in badges:
        badgeId.append(badge.badgeID)
        badgeName.append(badge.badgeName)
        badgeImage.append(badge.badgeImage)
        badgeDescription.append(badge.badgeDescription)
                    
        # The range part is the index numbers.
    context_dict['badgesInfo'] = zip(range(1,badges.count()+1),badgeId,badgeName,badgeImage, badgeDescription)

    #return render(request,'Badges/ListBadges.html', context_dict)
    return render(request,'Badges/Badges.html', context_dict)