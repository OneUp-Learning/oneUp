from django.template import RequestContext
from django.shortcuts import render
from Instructors.models import Challenges, Courses
from Students.models import Student, StudentChallenges

from django.contrib.auth.decorators import login_required

@login_required
def ChallengeDescription(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict = { }
    
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
    
    # check if course was selected
    if not 'currentCourseID' in request.session:
        context_dict['course_Name'] = 'Not Selected'
        context_dict['course_notselected'] = 'Please select a course'
    else:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
        
        string_attributes = ['challengeName','courseID','isGraded',                 #'challengeCategory','timeLimit','numberAttempts',
                      'challengeAuthor',
                      'feedbackOption1','feedbackOption2','feedbackOption3',
                      'challengeDifficulty', 'challengePassword']; # Added challengePassword AH

     
        if request.GET:
                       
            # Getting the challenge information which the student has selected
            if request.GET['challengeID']:
                #studentId = 1; # for now student id is 1 as there is no login table.. else studentd id will be the login ID that we get from the cookie or session
                studentId = Student.objects.filter(user=request.user)
                
                challengeId = request.GET['challengeID']
                challenge = Challenges.objects.get(pk=int(challengeId))
                
                data = getattr(challenge,'timeLimit')
                if data == 999999:
                    context_dict['timeLimit'] = "no time limit"
                else:
                    context_dict['timeLimit']= data
                    
                data = getattr(challenge,'numberAttempts')
                print(str(data))
                if data == 999999:
                    context_dict['numberAttempts'] = "unlimited"
                else:
                    context_dict['numberAttempts']= data

                    
                context_dict['challengeID'] = challengeId
                for attr in string_attributes:
                    context_dict[attr] = getattr(challenge, attr)

                total_attempts = challenge.numberAttempts
                if data == 999999:
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
               
            # Copy all of the attribute values into the context_dict to
            # display them on the page.
            
    return render(request,'Students/ChallengeDescription.html', context_dict)
