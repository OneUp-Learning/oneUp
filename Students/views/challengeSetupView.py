from django.shortcuts import render
from django.template import RequestContext
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import random 

from time import strftime

from Instructors.models import Challenges, Courses, Answers
from Instructors.models import ChallengesQuestions, MatchingAnswers, StaticQuestions
from Students.models import Student, StudentRegisteredCourses
from Badges.events import register_event
from Badges.enums import Event

@login_required
def ChallengeSetup(request):
 
    context_dict = { }
    
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username      
    
    # check if course was selected
    if not 'currentCourseID' in request.session:
        context_dict['course_Name'] = 'Not Selected'
        context_dict['course_notselected'] = 'Please select a course'
    else:
    #Displaying the questions in the challenge which the student has opted 
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
        student = Student.objects.get(user=request.user)   
        st_crs = StudentRegisteredCourses.objects.get(studentID=student,courseID=currentCourse)
        context_dict['avatar'] = st_crs.avatarImage                  
        
        questionObjects= []
                
        if request.POST:        
            if request.POST['challengeId']: 
                challengeId = request.POST['challengeId']
                context_dict['challengeID']= challengeId
                challenge = Challenges.objects.get(pk=int(request.POST['challengeId']))
                context_dict['challengeName'] = challenge.challengeName
                print(challengeId)
                # Checks if password was entered correctly
                if challenge.challengePassword != '':
                    if 'password' not in request.POST or request.POST['password'] != challenge.challengePassword:
                        return redirect('/oneUp/students/ChallengeDescription?challengeID=' + challengeId)
                challenge_questions = ChallengesQuestions.objects.filter(challengeID=challengeId)
                for challenge_question in challenge_questions:
                    print("challenge_question.questionID: "+str(challenge_question.questionID))
                    questionObjects.append(challenge_question.questionID)
                
                #getting all the question of the challenge except the matching question
                challengeDetails = Challenges.objects.filter(challengeID = challengeId)
                qlist = []
                for q in questionObjects:
                    questdict = q.__dict__
                    answers = Answers.objects.filter(questionID = q.questionID)
                    answer_range = range(1,len(answers)+1)
                    questdict['answers_with_count'] = zip(answer_range,answers)
                    questdict['typeID']=str(q.type)
                    
                    staticQuestion = StaticQuestions.objects.get(pk=q.questionID)
                    questdict['questionText']=staticQuestion.questionText
                    print('questionText = ' + staticQuestion.questionText)
                    print(questdict)
                    for duration in challengeDetails:
                        questdict['testDuration']=duration.timeLimit
                    
                    #getting the matching questions of the challenge from database
                    matchlist = []
                    match_shuffle_list = []
                    for match in MatchingAnswers.objects.filter(questionID=q.questionID):
                        matchdict = match.__dict__
                        #match_shuffle_list.append(match.matchingAnswerText)
                        matchdict['answers_count'] = range(1,len(answers)+1)
                        #ans_range = range(1,len(answers)+1)
                        #matchdict['match_answers'] = zip(ans_range,match_shuffle_list)
                        matchlist.append(matchdict)
                    
                    random.shuffle(matchlist)
                    questdict['matches']=matchlist
                    qlist.append(questdict)
                
            context_dict['question_range'] = zip(range(1,len(questionObjects)+1),qlist)
            context_dict['startTime'] = strftime("%Y-%m-%d %H:%M:%S")
            
        register_event(Event.startChallenge,request,None,challengeId)
        print("Registered Event: Start Challenge Event, Student: student in the request, Challenge: " + challengeId)
        
    return render(request,'Students/ChallengeSetup.html', context_dict)

