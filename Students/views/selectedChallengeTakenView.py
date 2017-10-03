'''
Created on Sep 6, 2014

@author: Swapna
'''
from django.shortcuts import render

from Instructors.models import Answers, CorrectAnswers, MatchingAnswers, Challenges, StaticQuestions, DynamicQuestions
from Students.models import StudentChallenges, StudentChallengeQuestions, StudentChallengeAnswers
from Students.views.utils import studentInitialContextDict

from django.contrib.auth.decorators import login_required
from Badges.enums import staticQuestionTypesSet, QuestionTypes
from Instructors.lupaQuestion import lupa_available, CodeSegment, LupaQuestion
from Instructors.views.dynamicQuestionView import makeLibs
from Instructors.views.challengeListView import warmUpChallengeList

@login_required
def SelectedChallengeTaken(request):
 
    context_dict,currentCourse = studentInitialContextDict(request)
    
    context_dict['questionTypes'] = QuestionTypes
    
    #Displaying the questions in the challenge which the student has opted 
    if 'currentCourseID' in request.session:    
       
        questionObjects= []
        
        useranswerObjects = []
        matchanswerObjects = []
        useranswerIds = []
        questionScoreObjects = []
        questionTotalObjects = []
        entireScore = 0
        
        
        if 'warmUp' in request.GET:
            context_dict['warmUp'] = 1
           
        
        if request.GET:
            # Getting the challenge information which the student has selected
            if 'studentChallengeID' in request.GET:  
                studentChallengeId = request.GET['studentChallengeID']
                context_dict['studentChallengeID'] = request.GET['studentChallengeID']
                   
            else:
                student = context_dict['student']
                challenge = Challenges.objects.get(pk=int(request.GET['challengeID']))
                studentChallengeId = StudentChallenges.objects.filter(studentID=student, courseID=currentCourse,challengeID=challenge.challengeID)
                 
            challengeId = request.GET['challengeID']
            chall = Challenges.objects.get(pk=int(challengeId))
            challengeName = chall.challengeName
            
            studentChallenges = StudentChallenges.objects.filter( courseID=currentCourse,challengeID=challengeId)
                 
            for Schallenges in studentChallenges:
                if int(Schallenges.challengeID.challengeID) == int(challengeId):
                    entireScore = Schallenges.testScore
            
            qlist = []
            
            challenge_questions = StudentChallengeQuestions.objects.filter(studentChallengeID=studentChallengeId)
            for challenge_question in challenge_questions:
                print("challenge_question.questionID: "+str(challenge_question.questionID))
                questionObjects.append(challenge_question.questionID)
                questionScoreObjects.append(challenge_question.questionScore)
                questionTotalObjects.append(challenge_question.questionTotal)
                useranswerIds.append(challenge_question.studentChallengeQuestionID)

                studentAnswers = StudentChallengeAnswers.objects.filter(studentChallengeQuestionID=challenge_question)
                match_list = MatchingAnswers.objects.filter(questionID=challenge_question.questionID)
                
                matchanswerObjects.append(match_list)
                
                q = challenge_question.questionID
                questdict = q.__dict__
                
                answers = Answers.objects.filter(questionID = q.questionID)
                answer_range = range(1,len(answers)+1)
                questdict['answers_with_count'] = zip(answer_range,answers)  
                questdict['match_with_count'] = zip(answer_range,answers) 
                questdict['challengeID']= challengeId

                if q.type == QuestionTypes.matching:
                    userAnswerDict = {}                
                    for stuAns in studentAnswers:
                        matchAnswer = stuAns.studentAnswer
                        parts = matchAnswer.split(':')
                        userAnswerDict[int(parts[1])] = MatchingAnswers.objects.get(pk=parts[0]).matchingAnswerText
                    useranswerObjects.append([userAnswerDict[ans.answerID] for ans in answers])                  
                else:
                    answer_list = []
                    for stuAns in studentAnswers:
                        answer_list.append(stuAns.studentAnswer)
                    useranswerObjects.append(answer_list)

                print("user answers:"+str(useranswerObjects))

                if q.type in staticQuestionTypesSet:
                    staticQuestion = StaticQuestions.objects.get(pk=q.questionID)
                    questdict['questionText']=staticQuestion.questionText
                else:
                    dynamicQuestion = DynamicQuestions.objects.get(pk=q.questionID)
                    if not lupa_available:
                        questdict['questionText'] = "<B>Lupa not installed.  Please ask your server administrator to install it to enable dynamic problems.</B>"
                    else:
                        seed = challenge_question.seed                      
                        code = [CodeSegment.new(CodeSegment.raw_lua,dynamicQuestion.code,"")]
                        numParts = dynamicQuestion.numParts
                        libs = makeLibs(dynamicQuestion)
                        part = 1
                        lupaQuest = LupaQuestion(code, libs, seed, "dummy_uniqid", numParts)
                        questdict['questionText'] = lupaQuest.getQuestionPart(1)
                
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
            context_dict['entireScore'] = entireScore        
            context_dict['question_range'] = zip(range(1,len(questionObjects)+1),qlist,useranswerObjects,matchanswerObjects,questionScoreObjects,questionTotalObjects )
               
    return render(request,'Students/SelectedChallengeTaken.html', context_dict)

