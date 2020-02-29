#
# Created on  10/30/2015
# Dillon Perry
#Page unemployed 2/28/20
"""
from django.template import RequestContext
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test

from Instructors.models import Milestones
from Instructors.views.utils import initialContextDict
from Instructors.views.milestoneListView import createContextForMilestoneList
from oneUp.decorators import instructorsCheck     

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')
def milestoneCreateView(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict, currentCourse = initialContextDict(request)

    # In this class, these are the names of the attributes which are strings.
    # We put them in an array so that we can copy them from one item to
    # another programmatically instead of listing them out.
    string_attributes = ['milestoneName','description','points'];

    # prepare context for Milestone List      
    context_dict = createContextForMilestoneList(request, context_dict, currentCourse)

    if request.POST:

        # Get the milestone from the DB for editing or create a new milestone  
        if 'milestoneID' in request.POST:
            mi = request.POST['milestoneID']
            milestone = Milestones.objects.get(pk=int(mi))
        else:
            milestone = Milestones()

        # Copy all strings from POST to database object.
        for attr in string_attributes:
            setattr(milestone,attr,request.POST[attr])
                   
       # get the author                            
        if request.user.is_authenticated:
            milestone.authorID = request.user
        else:
            milestone.author = ""

        milestone.courseID = currentCourse 

        milestone.save();  #Writes to database.
         
                
        return redirect('milestoneList')

    else:
        if request.GET:
                            
            # If questionId is specified then we load for editing.
            if 'milestoneID' in request.GET:
                milestone = Milestones.objects.get(pk=int(request.GET['milestoneID']))

                # Copy all of the attribute values into the context_dict to
                # display them on the page.
                context_dict['milestoneID'] = request.GET['milestoneID']
                
                for attr in string_attributes:
                    context_dict[attr]=getattr(milestone,attr)

    return render(request,'Instructors/MilestoneCreateForm.html', context_dict)
    """
