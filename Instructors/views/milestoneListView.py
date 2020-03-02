#Page unemployed 2/28/20
'''
Created on October, 2015

@author: Dillon Perry

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from Instructors.models import Milestones
from Instructors.views.utils import initialContextDict
from oneUp.decorators import instructorsCheck     


def createContextForMilestoneList(request, context_dict, currentCourse):
    milestone_ID = []      
    milestone_Name = []         
    description = []
    points = []
        
    milestones = Milestones.objects.filter(courseID=currentCourse)
    for milestone in milestones:
        milestone_ID.append(milestone.milestoneID) #pk
        milestone_Name.append(milestone.milestoneName)
        description.append(milestone.description[:100])
        points.append(milestone.points)
                    
    # The range part is the index numbers.
    context_dict['milestone_range'] = zip(range(1,milestones.count()+1),milestone_ID,milestone_Name,description,points)
    return context_dict

    
@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')  
def milestoneList(request):
    context_dict, currentCourse = initialContextDict(request)
    context_dict = createContextForMilestoneList(request, context_dict, currentCourse)

    return render(request,'Instructors/MilestonesList.html', context_dict)
    '''
