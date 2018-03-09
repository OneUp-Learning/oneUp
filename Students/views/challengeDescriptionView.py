import datetime
from django.shortcuts import render
from Instructors.models import Challenges 
from Instructors.views.utils import utcDate
from Instructors.constants import default_time_str
from Students.models import Student, StudentChallenges
from Students.views.utils import studentInitialContextDict
from django.db.models import Q
from time import strftime
from django.contrib.auth.decorators import login_required

@login_required
def ChallengeDescription(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.

    context_dict,currentCourse = studentInitialContextDict(request)                 

    if 'currentCourseID' in request.session:   
        chall_ID = []      
        chall_Name = []  
        defaultTime = utcDate(default_time_str, "%m/%d/%Y %I:%M:%S %p")
        currentTime = utcDate()   
        string_attributes = ['challengeName','courseID','isGraded',                 #'challengeCategory','timeLimit','numberAttempts',
                      'challengeAuthor',
                      'displayCorrectAnswer','displayCorrectAnswerFeedback','displayIncorrectAnswerFeedback',
                      'challengeDifficulty', 'challengePassword','isVisible']; # Added challengePassword AH

        challenges = Challenges.objects.filter(courseID=currentCourse,  isVisible=True).filter(Q(startTimestamp__lt=currentTime) | Q(startTimestamp=defaultTime), Q(endTimestamp__gt=currentTime) | Q(endTimestamp=defaultTime))
        
        
                
        if request.GET:
                       
            # Getting the challenge information which the student has selected
            if request.GET['challengeID']:
                #studentId = 1; # for now student id is 1 as there is no login table.. else studentd id will be the login ID that we get from the cookie or session
                
                if request.GET['isWarmup']:
                    context_dict['isWarmup'] = request.GET['isWarmup']
                else:
                    context_dict['isWarmup'] = False
                    
                studentId = Student.objects.filter(user=request.user)
                
                challengeId = request.GET['challengeID']
                challenge = Challenges.objects.get(pk=int(challengeId))
                
                if challenge in challenges:
                    context_dict['available'] = "This challenge can be taken"
                else:
                    context_dict['unAvailable'] = "This challenge can not be taken at this time "    
                
                data = getattr(challenge,'timeLimit')
                if data == 99999:
                    context_dict['timeLimit'] = "no time limit"
                else:
                    context_dict['timeLimit']= data
                    
                data = getattr(challenge,'numberAttempts')
                print(str(data))
                if data == 99999:
                    context_dict['numberAttempts'] = "unlimited"
                else:
                    context_dict['numberAttempts']= data
                
                context_dict['challengeID'] = challengeId
                for attr in string_attributes:
                    context_dict[attr] = getattr(challenge, attr)
                    
                total_attempts = challenge.numberAttempts
                if data == 99999:
                    context_dict['more_attempts'] = "unlimited"
                else:                             
                    # getting the number of attempts to check if the student is out of attempts
                    student_attempts = StudentChallenges.objects.filter(studentID=studentId, challengeID=challengeId) 
                    
                    if int(len(student_attempts)) < (int(total_attempts) - 1):
                        # student has more than one attempt
                        context_dict['more_attempts'] = '' + str(int(total_attempts) - int(len(student_attempts))) + ''
                        
                    elif int(len(student_attempts)) == (int(total_attempts) - 1):
                        # last attempt of the student
                        context_dict['last_attempt'] = 'This is your last attempt!!!'
                                            
                    elif int(len(student_attempts)) > (int(total_attempts) - 1):
                        # no more attempts left
                        context_dict['no_attempt'] = "Sorry!! You don't have any more attempts left"
                 
                 
                 
                 
    return render(request,'Students/ChallengeDescription.html', context_dict)
