'''
Created on Nov 3, 2016

@author: Austin Hodge
'''

from django.shortcuts import render

from Badges.models import Badges, Courses
from Students.models import Student, StudentRegisteredCourses

from django.contrib.auth.decorators import login_required

@login_required
def BadgesDisplay(request):
 
    context_dict = { }
    
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username        
    
    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
        student = Student.objects.get(user=request.user)   
        st_crs = StudentRegisteredCourses.objects.get(studentID=student,courseID=currentCourse)
        context_dict['avatar'] = st_crs.avatarImage                  
    else:
        context_dict['course_Name'] = 'Not Selected'
        
    badgeId = [] 
    badgeName = []
    badgeImage = []
    badgeDescription = []
        
        #Displaying the list of challenges from database
    #badges = Badges.objects.all()
    badges = Badges.objects.filter(courseID=currentCourse)
    for badge in badges:
        badgeId.append(badge.badgeID)
        badgeName.append(badge.badgeName)
        badgeImage.append(badge.badgeImage)
        badgeDescription.append(badge.badgeDescription)
                    
        # The range part is the index numbers.
    context_dict['badgesInfo'] = zip(range(1,badges.count()+1),badgeId,badgeName,badgeImage, badgeDescription)

    #return render(request,'Badges/ListBadges.html', context_dict)
    return render(request,'Students/CourseBadges.html', context_dict)