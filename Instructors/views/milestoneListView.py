'''
Created on October, 2015

@author: Dillon Perry
'''
from django.template import RequestContext
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Instructors.models import Milestones, Courses

def createContextForMilestoneList():
    context_dict = { }

    milestone_ID = []      
    milestone_Name = []         
    description = []
    points = []
        
    milestones = Milestones.objects.all()
    for milestone in milestones:
        milestone_ID.append(milestone.milestoneID) #pk
        milestone_Name.append(milestone.milestoneName)
        description.append(milestone.description[:100])
        points.append(milestone.points)
                    
    # The range part is the index numbers.
    context_dict['milestone_range'] = zip(range(1,milestones.count()+1),milestone_ID,milestone_Name,description,points)
    return context_dict

    
@login_required
def milestoneList(request):

 
    context_dict = createContextForMilestoneList()

    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username

    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected'
        

    return render(request,'Instructors/MilestonesList.html', context_dict)
