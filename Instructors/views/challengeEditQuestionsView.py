from django.template import RequestContext
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from Instructors.models import Challenges, Courses
from Instructors.views.challengeListView import makeContextDictForQuestionsInChallenge


@login_required
def challengeEditQuestionsView(request):
 
    context_dict = { }
        
    if 'challengeID' in request.GET:       
        if Challenges.objects.filter(challengeID = request.GET['challengeID'],challengeName="Unassigned Problems"):
            context_dict["unassign"]= 1
        context_dict = makeContextDictForQuestionsInChallenge(request.GET['challengeID'], context_dict)
        
        challenge = Challenges.objects.get(pk=int(request.GET['challengeID']))
    
        # Add check to see if the problem is a warmUp or Serious Challenge -AH
        if challenge.isGraded:
            context_dict['serious'] = True
        else:
            context_dict['warmUp'] = True
                           
    if 'problems' in request.GET:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict["unassign"]= 1
        chall=Challenges.objects.filter(challengeName="Unassigned Problems",courseID=currentCourse)
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

  

