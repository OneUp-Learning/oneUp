from django.template import RequestContext
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from Instructors.models import Challenges, Courses
from Instructors.views.challengeListView import makeContextDictForQuestionsInChallenge
from Instructors.lupaQuestion import lupa_available
from Instructors.constants import unassigned_problems_challenge_name

@login_required
def challengeEditQuestionsView(request):
 
    context_dict = { }
    context_dict['lupa_available'] = lupa_available
        
    if 'challengeID' in request.GET:   
        challenge = Challenges.objects.get(pk=int(request.GET['challengeID']))    
        if Challenges.objects.filter(challengeID = request.GET['challengeID'],challengeName=unassigned_problems_challenge_name):
            context_dict["unassign"]= 1
            context_dict['serious'] = False
            context_dict['warmUp'] = False
        else:
            if challenge.isGraded:
                context_dict['serious'] = True
            else:
                context_dict['warmUp'] = True
        context_dict = makeContextDictForQuestionsInChallenge(request.GET['challengeID'], context_dict)
        
        
                                       
    if 'problems' in request.GET:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict["unassign"]= 1
        chall=Challenges.objects.filter(challengeName=unassigned_problems_challenge_name,courseID=currentCourse)
        for challID in chall:
            challengeID = (str(challID.challengeID))   
        
        #return redirect('/oneUp/instructors/challengeQuestionsList?challengeID=' + challengeID, context_dict) 
        context_dict = makeContextDictForQuestionsInChallenge(challengeID, context_dict)

    
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
 
    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected'  
    
    return render(request,'Instructors/ChallengeQuestionsList.html', context_dict)

  

