'''
Created on Jun 12, 2014
Updated May/10/2017

@author: iiscs
'''
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from time import strftime

from Instructors.models import Questions, StaticQuestions, Answers, CorrectAnswers, Challenges, Courses
from Instructors.models import ChallengesQuestions, MatchingAnswers, QuestionsSkills
from Students.models import StudentCourseSkills, Student, StudentChallenges, StudentChallengeQuestions, StudentChallengeAnswers, MatchShuffledAnswers
from Students.views.utils import studentInitialContextDict
from Badges.events import register_event
from Badges.enums import Event, QuestionTypes, dynamicQuestionTypesSet
from django.template.context_processors import request

def saveSkillPoints(questionId, challengeId, studentId, studentChallengeQuestion):

    # get all skills to which this question contributes
    questionSkills = QuestionsSkills.objects.filter(questionID=questionId, challengeID=challengeId)
    if questionSkills:
        for qskill in questionSkills:

            #check if this question has already been answered and contributed to the skill
            #qss is all appearances of this question in StudentCourseSkills 
            qss = StudentCourseSkills.objects.filter(studentChallengeQuestionID__questionID__questionID=questionId, studentChallengeQuestionID__studentChallengeID__studentID=studentId, skillID=qskill.skillID)

            if not qss:
                studentCourseSkills = StudentCourseSkills()
                studentCourseSkills.studentChallengeQuestionID = studentChallengeQuestion
                studentCourseSkills.skillID = qskill.skillID
                studentCourseSkills.skillPoints = qskill.questionSkillPoints 
                studentCourseSkills.save()
                
    return

def saveChallengeQuestion(studentChallenge, key, ma_point, c_ques_points, instructorFeedback):
    
    studentChallengeQuestion = StudentChallengeQuestions()
    studentChallengeQuestion.studentChallengeID = studentChallenge
    studentChallengeQuestion.questionID = Questions(key)
    studentChallengeQuestion.questionScore = ma_point
    studentChallengeQuestion.questionTotal = c_ques_points
    studentChallengeQuestion.usedHint = "False"
    studentChallengeQuestion.instructorFeedback = instructorFeedback
    studentChallengeQuestion.save()

    return studentChallengeQuestion

@login_required
def ChallengeResults(request):
  
    context_dict,currentCourse = studentInitialContextDict(request)                 

    if 'currentCourseID' in request.session:            
        user_dict = { } #dictionary to store user answers, grade them (except for matching) and send them to html page  
        match_sorted = {} #dictionary for saving the sorted order of the matching answer texts and also using it while grading
        instructorFeedback = "None" #Intially by default its saved none.. Updated after instructor's evaluation
        match_question_dict = {} #dictionary for saving matching answers order that were shuffled in the test display page 
        questionScore_dict = {} #dictionary for saving student's individual question score
        questionTotal_dict = {} #dictionary for saving individual question total score

        context_dict['questionTypes']= QuestionTypes
        
        #Displaying the score and the user and correct answers
        
        questionObjects= []
        useranswerObjects = []
        matchquestionObjects = []
        q_ID = []      # ID for questions
        score_list = []
        total_list = []
        questionScore_list = []
        questionTotal_list = []
        
        score=0
        total=0
        
        if request.POST:      
            
            if request.POST['challengeId'] == "":
                # Challenge without questions
                print('here')
                print(request.POST['challengeId'])
                return redirect('/oneUp/students/ChallengesList')
            
            else: 
                studentId = Student.objects.get(user=request.user)
                #print (studentId)
                
                currentCourseId = request.session['currentCourseID']
                challengeId = request.POST['challengeId']
                course = Courses.objects.get(pk=int(currentCourseId))
                challenge = Challenges.objects.get(pk=int(request.POST['challengeId']))
                context_dict['challengeName'] = challenge.challengeName
                
                if not challenge.isGraded:
                    print ("warmUp")
                    context_dict['warmUp'] = 1
                    
                print("Start Time:"+request.POST['startTime'])
                startTime = request.POST['startTime']    
                #end time of the test is the current time when it is navigated to this page
                endTime = strftime("%Y-%m-%d %H:%M:%S") #the end time is in yyyy-mm-dd hh:mm:ss format similar to start time
                print("End Time:"+str(endTime))

                attemptId = 'challenge:'+challengeId + '@' + startTime
                print("attemptID = "+attemptId)               
                
                if StudentChallenges.objects.filter(challengeID=challengeId,studentID=studentId,startTimestamp=endTime).count() > 0:
                    return redirect('/oneUp/students/ChallengeDescription?challengeID=' + challengeId)
                    
                #save initial student-challenge information pair (no score)to db
                studentChallenge = StudentChallenges()
                studentChallenge.studentID = studentId
                studentChallenge.courseID = course
                studentChallenge.challengeID = challenge
                studentChallenge.startTimestamp = startTime
                studentChallenge.endTimestamp = endTime
                studentChallenge.testScore = 0 #initially its zero and updated after calculation at the end
                studentChallenge.testTotal = 0 #initially its zero and updated after calculation at the end
                studentChallenge.instructorFeedback = instructorFeedback
                studentChallenge.save()
                                
                sessionDict = request.session[attemptId]
                if not sessionDict:
                    #TODO: make appropriate error message for here.
                    print("challenge result requested for challenge not begun.")

                questions = sessionDict['questions']
                context_dict["questionCount"] = len(questions)
                questionsDict = {}
                totalStudentScore = 0
                totalPossibleScore = 0
                
                for question in questions:
                    questionType = question['question']['type']        
                    if questionType == QuestionTypes.multipleChoice:
                        answerInputName = str(question['index']) + '-ans'
                        correctAnswer = CorrectAnswers.objects.get(questionID=question['question']['questionID']).answerID
                        correctAnswerText = correctAnswer.answerText
                        question['correct_answer_text'] = correctAnswerText
                        if answerInputName not in request.POST:
                            question['user_points'] = 0
                            question['user_answer'] = {'answerNumber':"",'answerText':"No answer"}
                        else:
                            userSelection = int(request.POST[answerInputName])
                            userAnswer = question['answers'][userSelection-1] # Convert from 1-indexed to 0-indexed
                            question['user_answer'] = {'answerNumber':userSelection,'answerText':userAnswer['answerText']}
                            if userAnswer['answerID'] == correctAnswer.answerID:
                                question['user_points'] = question['total_points']
                            else:
                                question['user_points'] = 0
                            studentAnswerList = [str(userAnswer['answerID'])]
                    elif questionType == QuestionTypes.multipleAnswers:
                        answerInputName = str(question['index']) + '-ans[]'
                        correctAnswers = [x.answerID for x in CorrectAnswers.objects.filter(questionID=question['question']['questionID'])]
                        correctAnswerIds = [x.answerID for x in correctAnswers]
                        question['correct_answer_texts'] = [x.answerText for x in correctAnswers]
                        
                        userAnswerIndexes = request.POST.getlist(answerInputName)
                        # convert all to ints.
                        userAnswerIndexes = [int(x) for x in userAnswerIndexes]

                        userAnswerIds = [question['answers'][x-1]['answerID'] for x in userAnswerIndexes]
                        valuePerAnswer = question['total_points']/len(question['answers'])
                        numAnswersIncorrect = len([x for x in userAnswerIds if x not in correctAnswerIds])
                        numAnswersMissing = len([x for x in correctAnswerIds if x not in userAnswerIds])
                        question['user_points'] = question['total_points']-valuePerAnswer*(numAnswersIncorrect+numAnswersMissing)
                        question['user_answers'] = [{'answerNumber':x,'answerText':question['answers'][x-1]['answerText']} for x in userAnswerIndexes]
                        studentAnswerList = userAnswerIds
                    elif questionType == QuestionTypes.matching:
                        # Find the index for each correct matching answer
                        valuePerAnswer = question['total_points']/len(question['answers'])
                        userScore = 0
                        userAnswers = []
                        studentAnswerList = []

                        i = 1                        
                        matches = question['matches']
                        for match in matches:
                            if match is not None:
                                # Find correct answer
                                for index,answer in question['answers_with_count']:
                                    if answer['answerID'] == match['answerID_id']:
                                        correctAnswerIndex = index
                                        break # Skip remainder of this inner for loop
                                
                                answerInputName = str(question['index'])+'-'+str(i)
                                i = i + 1
                                userAnswerIndex = int(request.POST[answerInputName])
                                userAnswers.append( {'answerNumber':userAnswerIndex,'answerText':question['answers'][userAnswerIndex-1]['answerText']} )
                                if correctAnswerIndex == userAnswerIndex:
                                    userScore = userScore + valuePerAnswer
                                    studentAnswerList.append(str(match['matchingAnswerID'])+":"+str(question['answers'][userAnswerIndex-1]['answerID']))

                        question['user_points'] = userScore
                        question['user_answers'] = userAnswers
                    elif questionType == QuestionTypes.trueFalse:
                        answerInputName = str(question['index'])+'-ans'
                        if answerInputName not in request.POST:
                            question['user_points'] = 0
                            question['user_answer'] = {'answerNumber':"",'answerText':"No answer"}
                            userAnswerValue = ""
                        else:
                            userAnswerValue = request.POST[answerInputName] == 't'
                            question['user_answer'] = {'answerText':str(userAnswerValue),'answerValue':userAnswerValue}
                            correctAnswerValue = CorrectAnswers.objects.get(questionID=question['question']['questionID']).answerID.answerText == "True"
                            if userAnswerValue == correctAnswerValue:
                                question['user_points'] = question['total_points']
                            else:
                                question['user_points'] = 0
                        studentAnswerList = [str(userAnswerValue)]
                        question['correctAnswerText'] = str(correctAnswerValue)
                    elif questionType == QuestionTypes.essay:
                        question['user_points']=0
                        question['user_answer']=request.POST[question['index']+'-ans']
                        studentAnswerList = [question['user_answer']]
                    elif questionType in dynamicQuestionTypesSet:
                        print("TODO: This dynamic question part")
                    
                    totalStudentScore += question['user_points']
                    totalPossibleScore += question['total_points']
                    studentChallengeQuestion = saveChallengeQuestion(studentChallenge, question['question']['questionID'], question['user_points'], question['total_points'], "")
                    for studentAnswer in studentAnswerList:
                        studentChallengeAnswers = StudentChallengeAnswers()
                        studentChallengeAnswers.studentChallengeQuestionID = studentChallengeQuestion
                        studentChallengeAnswers.studentAnswer = studentAnswer
                        studentChallengeAnswers.save()

                # The sort on the next line should be unnecessary, but better safe than sorry
                context_dict['questions'] = sorted(questions,key=lambda q:q['index'])
                context_dict['total_user_points'] = totalStudentScore
                context_dict['total_possible_points'] = totalPossibleScore

                studentChallenge.testScore = totalStudentScore
                studentChallenge.testTotal = totalPossibleScore
                studentChallenge.save()
                
                register_event(Event.endChallenge,request,studentId,challengeId)

    return render(request,'Students/ChallengeResults.html', context_dict)

