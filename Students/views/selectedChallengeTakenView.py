'''
Created on Sep 6, 2014

@author: Swapna
'''
from django.shortcuts import render

from django.template import RequestContext
from django.shortcuts import render

from Instructors.models import Answers, CorrectAnswers, MatchingAnswers, Courses, Challenges, StaticQuestions
from Students.models import Student, StudentChallenges, StudentChallengeQuestions, StudentChallengeAnswers, MatchShuffledAnswers, StudentRegisteredCourses
import random 
from _ctypes import Array
from _ast import Str
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

@login_required
def SelectedChallengeTaken(request):
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
        student = Student.objects.get(user=request.user)   
        st_crs = StudentRegisteredCourses.objects.get(studentID=student,courseID=currentCourse)
        context_dict['avatar'] = st_crs.avatarImage          
        
        #Displaying the questions in the challenge which the student has opted 
        
        questionObjects= []
        
        useranswerObjects = []
        matchanswerObjects = []
        useranswerIds = []
        questionScoreObjects = []
        questionTotalObjects = []
        
        if 'warmUp' in request.GET:
            context_dict['warmUp'] = 1
        
        if request.GET:
            # Getting the challenge information which the student has selected
            if 'studentChallengeID' in request.GET:  
                studentChallengeId = request.GET['studentChallengeID']
                context_dict['studentChallengeID'] = request.GET['studentChallengeID']
            else:
                user = User.objects.filter(username=request.GET['userID'])
                studentId = Student.objects.filter(user=user)
                challenge = Challenges.objects.get(pk=int(request.GET['challengeID']))
                studentChallengeId = StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse,challengeID=challenge.challengeID)
                
            challengeId = request.GET['challengeID']
            #challengeName = 
            chall = Challenges.objects.get(pk=int(challengeId))
            challengeName = chall.challengeName
            
            
            challenge_questions = StudentChallengeQuestions.objects.filter(studentChallengeID=studentChallengeId)
            print('here',challenge_questions)
            for challenge_question in challenge_questions:
                print("challenge_question.questionID: "+str(challenge_question.questionID))
                questionObjects.append(challenge_question.questionID)
                questionScoreObjects.append(challenge_question.questionScore)
                questionTotalObjects.append(challenge_question.questionTotal)
                useranswerIds.append(challenge_question.studentChallengeQuestionID)
            print("Answer ids:"+str(useranswerIds))
            
            #student_answers = StudentChallengeAnswers.objects.filter(studentChallengeQuestionID = (StudentChallengeQuestions.objects.filter(studentChallengeID=studentChallengeId)))
            for answer_Id in useranswerIds:
                answer_list = []
                match_list = []
                #studentAnswerId = StudentChallengeQuestions.objects.get(studentChallengeID=studentChallengeId, questionID=q)
                studentAnswers = StudentChallengeAnswers.objects.filter(studentChallengeQuestionID=answer_Id)
                matchShuffled = MatchShuffledAnswers.objects.filter(studentChallengeQuestionID=answer_Id)
                #if len(studentAnswer)>1:
                
                for stuAns in studentAnswers:
                    answer_list.append(stuAns.studentAnswer)
                useranswerObjects.append(answer_list)
                #else:
                #useranswerObjects.append(studentAnswer.studentAnswer)
                print("user answers:"+str(useranswerObjects))
                
                for matAns in matchShuffled:
                    match_list.append(matAns.MatchShuffledAnswerText)
                matchanswerObjects.append(match_list)
                #else:
                #useranswerObjects.append(studentAnswer.studentAnswer)
                print("user answers:"+str(matchanswerObjects))
                
            #getting all the question of the challenge except the matching question
            #challengeDetails = Challenges.objects.filter(challengeID = challengeId)
            qlist = []
            for q in questionObjects:
                questdict = q.__dict__
                
                answers = Answers.objects.filter(questionID = q.questionID)
                answer_range = range(1,len(answers)+1)
                questdict['answers_with_count'] = zip(answer_range,answers)  
                questdict['match_with_count'] = zip(answer_range,answers) 
                
                staticQuestion = StaticQuestions.objects.get(pk=q.questionID)
                questdict['questionText']=staticQuestion.questionText                                       
                questdict['typeID']=str(q.type)
                questdict['challengeID']= challengeId
                
                correct_answers = CorrectAnswers.objects.filter(questionID = q.questionID)
                canswer_range = range(1,len(correct_answers)+1)
                questdict['correct_answers'] = zip(canswer_range,correct_answers)
                
                
                #getting the matching questions of the challenge from database
                matchlist = []
                for match in MatchingAnswers.objects.filter(questionID=q.questionID):
                    matchdict = match.__dict__
                    matchdict['answers_count'] = range(1,int(len(answers))+1)
                    matchlist.append(matchdict)
                questdict['matches']=matchlist
                qlist.append(questdict)
            context_dict['challengeID']= challengeId
            context_dict['chall_Name'] = challengeName        
            context_dict['question_range'] = zip(range(1,len(questionObjects)+1),qlist,useranswerObjects,matchanswerObjects,questionScoreObjects,questionTotalObjects)
            
        


    
    return render(request,'Students/SelectedChallengeTaken.html', context_dict)

