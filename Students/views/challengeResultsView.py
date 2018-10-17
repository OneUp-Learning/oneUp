'''
Created on Jun 12, 2014
Updated May/10/2017

@author: iiscs
'''
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime
from Instructors.views.utils import utcDate
from Instructors.models import Questions, CorrectAnswers, Challenges, Courses, QuestionsSkills, Answers, MatchingAnswers, DynamicQuestions, StaticQuestions,\
    ChallengesQuestions
from Students.models import StudentCourseSkills, Student, StudentChallenges, StudentChallengeQuestions, StudentChallengeAnswers
from Students.views.utils import studentInitialContextDict
from Badges.events import register_event
from Badges.event_utils import updateLeaderboard
from Badges.enums import Event, QuestionTypes, dynamicQuestionTypesSet, staticQuestionTypesSet
from Instructors.lupaQuestion import LupaQuestion, lupa_available, CodeSegment
from Instructors.views.dynamicQuestionView import makeLibs
from Badges.systemVariables import logger
from Students.views.challengeSetupView import makeSerializableCopyOfDjangoObjectDictionary
import re
import math
from decimal import Decimal
from pickletools import decimalnl_long
from sqlparse.utils import indent

def saveSkillPoints(questionId, course, studentId, studentChallengeQuestion):

    # get all skills to which this question contributes
    questionSkills = QuestionsSkills.objects.filter(questionID=questionId, courseID=course)
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

def saveChallengeQuestion(studentChallenge, key, ma_point, c_ques_points, instructorFeedback,seed):
    
    studentChallengeQuestion = StudentChallengeQuestions()
    studentChallengeQuestion.studentChallengeID = studentChallenge
    studentChallengeQuestion.questionID = Questions(key)
    studentChallengeQuestion.questionScore = ma_point
    studentChallengeQuestion.questionTotal = c_ques_points
    studentChallengeQuestion.usedHint = "False"
    #studentChallengeQuestion.instructorFeedback = instructorFeedback
    studentChallengeQuestion.seed = seed
    studentChallengeQuestion.save()
    return studentChallengeQuestion

@login_required
def ChallengeResults(request):
  
    context_dict,currentCourse = studentInitialContextDict(request)                 

    if 'currentCourseID' in request.session:
         #Intially by default its saved none.. Updated after instructor's evaluation

        # This is included so that we can avoid magic numbers for question types in the template.
        context_dict['questionTypes']= QuestionTypes
        
        if request.POST:      
            
            if request.POST['challengeId'] == "":
                # Challenge without questions
                print('here')
                print(request.POST['challengeId'])
                return redirect('/oneUp/students/ChallengesList')
            
            else: 
                        
                studentId = Student.objects.get(user=request.user)
                #print (studentId)
                
                challengeId = request.POST['challengeId']
                course = Courses.objects.get(pk=currentCourse.courseID)
                challenge = Challenges.objects.get(pk=challengeId)
                context_dict['challengeName'] = challenge.challengeName
                #context_dict['instructorFeedback'] = challenge.instructorFeedback
                
                
                if not challenge.isGraded:
                    print ("warmUp")
                    context_dict['warmUp'] = 1
                    
                print("Start Time: "+request.POST['startTime'])
                startTime = utcDate(request.POST['startTime'], "%m/%d/%Y %I:%M:%S %p")  
                #end time of the test is the current time when it is navigated to this page
                endTime = utcDate()
                print("End Time:"+ endTime.strftime("%m/%d/%Y %I:%M %p"))

                attemptId = 'challenge:'+challengeId + '@' + startTime.strftime("%m/%d/%Y %I:%M:%S %p")
                print("attemptID = "+attemptId)               
                
                # Do not grade the same challenge twice
                if StudentChallenges.objects.filter(challengeID=challengeId,studentID=studentId,startTimestamp=startTime).count() > 0:
                    return redirect('/oneUp/students/ChallengeDescription?challengeID=' + challengeId)
                    
                #save initial student-challenge information pair (no score)to db
                studentChallenge = StudentChallenges()
                studentChallenge.studentID = studentId
                studentChallenge.courseID = course
                studentChallenge.challengeID = challenge
                studentChallenge.startTimestamp = startTime
                studentChallenge.endTimestamp = endTime
                studentChallenge.testScore = 0 #initially its zero and updated after calculation at the end
              #  studentChallenge.instructorFeedback = instructorFeedback 
                studentChallenge.save()
                
                #print(studentChallenge.endTimestamp - studentChallenge.startTimestamp)
                                
                sessionDict = request.session[attemptId]
                if not sessionDict:
                    context_dict['errorName'] = "Challenge not begun"
                    context_dict['errorMessage'] = "An attempt to submit challenge "+challenge.challengeName+" has occurred, but this system has " + \
                        "no record of that challenge begin taken."
                    return render(request, "Students/ChallengeError.html", context_dict)
                    print("challenge result requested for challenge not begun.")

                if (endTime - startTime).total_seconds() > (challenge.timeLimit+1) * 60: # We add a one minute fudge factor to account for things like network delays
                    context_dict['errorName'] = "Time Expired"
                    context_dict['errorMessage'] = "Time expired prior to the submission of this challenge."
                    return render(request, "Students/ChallengeError.html", context_dict)

                questions = sessionDict['questions']
                context_dict["questionCount"] = len(questions)
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
                        answerInputName = str(question['index']) + '-ans'
                        correctAnswers = [x.answerID for x in CorrectAnswers.objects.filter(questionID=question['question']['questionID'])]
                        correctAnswerIds = [x.answerID for x in correctAnswers]
                        question['correct_answer_texts'] = [x.answerText for x in correctAnswers]
                        
                        userAnswerIndexes = request.POST.getlist(answerInputName)
                        
                        if not userAnswerIndexes:
                            #user has not selected any answer
                            question['user_points'] = 0
                            question['user_answers'] = ""
                            userAnswerIds = []

                        else:                       
                            # convert all to ints.
                            userAnswerIndexes = [int(x) for x in userAnswerIndexes]   
                            userAnswerIds = [question['answers'][x-1]['answerID'] for x in userAnswerIndexes]
                            
                            valuePerAnswer = question['total_points']/len(question['answers'])
                            numAnswersIncorrect = len([x for x in userAnswerIds if x not in correctAnswerIds])                            
                            numAnswersMissing = len([x for x in correctAnswerIds if x not in userAnswerIds])
                        
                            question['user_points'] = round(question['total_points']-valuePerAnswer*(numAnswersIncorrect+numAnswersMissing), 2)
                            question['user_answers'] = [{'answerNumber':x,'answerText':question['answers'][x-1]['answerText']} for x in userAnswerIndexes]
                        
                        print('question[user_points] = ', question['user_points'])
                        
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
                        correctAnswerValue = CorrectAnswers.objects.get(questionID=question['question']['questionID']).answerID.answerText == "true"
                        if answerInputName not in request.POST:
                            question['user_points'] = 0
                            question['user_answer'] = {'answerNumber':"",'answerText':"No answer"}
                            userAnswerValue = ""
                        else:
                            userAnswerValue = request.POST[answerInputName] == 't'
                            question['user_answer'] = {'answerText':str(userAnswerValue),'answerValue':userAnswerValue}
                            print('userAnswerValue '+str(userAnswerValue))
                            print('correctAnswerValue ' + str(correctAnswerValue))
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
                        if not question['hasMultipleParts']:
                            lupaQuestion = LupaQuestion.createFromDump(question['lupaquestion'])
                            answers = {}
                            for value in request.POST:
                                indexstring = str(question['index'])
                                if (value.startswith(indexstring+"-")): 
                                    answers[value[len(indexstring)+1:]] = request.POST[value]
                            question['user_answers'] = answers
                            studentAnswerList = [key+":"+answers[key] for key in answers.keys()]
                            question['evaluations'] = lupaQuestion.answerQuestionPart(1, answers)
                            if question['evaluations']:
                                question['user_points'] = sum([eval['value'] for eval in question['evaluations']])
                            else:
                                question['user_points'] = 0
                        else:
                            studentAnswerList = []
                            question['user_points'] = 0
                    elif questionType == QuestionTypes.parsons:
                            #get the answer for the question
                            answer = Answers.objects.filter(questionID=question['question']['questionID'])
                            print("Model Solution: ", answer[0].answerText)
                            answer = answer[0].answerText
                            
                            #get the language information and indentation status
                            #remove the first line that keeps the data
                            searchString = re.search(r'Language:([^;]+);Indentation:([^;]+);', answer)
                            answer =  re.sub("##", "", answer)
                            indentation = searchString.group(2)
                            print("Indentation", indentation)
                            answer = answer.replace(searchString.group(0), "")
                            
                            answer =  re.sub("^ *\\t", "  ", answer)
            
                            #tokenizer characters ☃ and ¬
                            answer = re.sub("\n", "\n¬☃", answer)
                            answer = re.sub("^[ ]+?", "☃", answer)
                            
                            #we turn the student solution into a list
                            answer = [x.strip() for x in answer.split('¬')]
                            
                            #get how many spces there are in the first line
                            print("answer[0]",answer[0])
                            answer[0] = re.sub("☃"," ",answer[0])
                            leadingSpacesCount = len(answer[0]) - len(answer[0].lstrip(' '))
                            print("leading spaces", leadingSpacesCount)
                            
                            #give each string the new line
                            tabedanswer = []
                            lengthOfModelSolution = len(answer)
                            for index, line in enumerate(answer):
                                line = re.sub("☃", "", line)
                                line = re.sub(".*#distractor", "", line)
                                line = re.sub("^[ ]{" + str(leadingSpacesCount) + "}", "", line)
                                if index < len(answer)- 1:
                                    line = line +"\n"
                                tabedanswer.append(line)
                            
                            answer = ""
                            answer = answer.join(tabedanswer)
                                                        
                            question['model_solution'] = answer
                            
                            #get all the data from the webpage
                            #data is accessed through the index
                            lineIndent = request.POST[str(question['index'])+'lineIndent']
                            studentSolution = request.POST[str(question['index'])+'studentSol']
                            wrongPositionLineNumberbers = request.POST[str(question['index'])+'lineNo']
                            errorDescriptions = request.POST[str(question['index'])+'errorDescription']
                            correctLineCount = request.POST[str(question['index'])+'correctLineCount']
                            feedBackButtonClickCount= request.POST[str(question['index'])+'feedBackButtonClickCount']
                            
                            correctLineCount = int(correctLineCount)
                            feedBackButtonClickCount = int(feedBackButtonClickCount)
                            print("Correct Line Count", correctLineCount)
                            print("WrongPositionLineNumbers", wrongPositionLineNumberbers)
                            
                            studentAnswerList = []
                            
                            #if the student ddnt fill in any solution, zero points
                            if(studentSolution == ""):
                                question['user_points'] = 0
                                studentAnswerList.append(studentSolution) 
                            else:
                                ##regex student solution, putting ¬ where the 
                                ##lines of code are broken into sections
                                ##§ is how we know which lines are which
                                #¬ is used join, to create a list
                                print("StudentSolutonBeforeChanges", studentSolution)
                                studentSolution = re.sub(r"&lt;", "<", studentSolution)
                                studentSolution = re.sub(r"&gt;", ">", studentSolution)
                                studentSolution = re.sub(r"&quot;", "\"", studentSolution)
                                studentSolution = re.sub(r"&quot;", "\"", studentSolution)
                                studentSolution = re.sub(r"^&amp;nbsp;", "", studentSolution)
                                studentSolution = re.sub(r",&amp;nbsp;", "ℊ", studentSolution)
                                studentSolution = re.sub(r";,", ";§¬", studentSolution)
                                studentSolution = re.sub(r";,", ";§¬", studentSolution)
                                studentSolution = re.sub(r"},", "}§¬", studentSolution)
                                studentSolution = re.sub(r"{,", "{§¬", studentSolution)
                                studentSolution = re.sub(r"\),", ")§¬", studentSolution)
                                studentSolution = re.sub(r"\(,", "(§¬", studentSolution)
                                print("StudentSolAfter change", studentSolution)
                                
                                #we turn the student solution into a list
                                studentSolution = [x.strip() for x in studentSolution.split('¬')]
                                studentSolutionLineCount = len(studentSolution)
                                
                                #make a list of lines, split on , so we know how much to indent where
                                lineIndent = [x.strip() for x in lineIndent.split(',')]
                                print("LineIndent", lineIndent);
                               
                                #perform the spacing for each line
                                IndentedStudentSolution = [];
                                for index, line in enumerate(studentSolution):
                                    line = '    ' * int(lineIndent[index]) + line
                                    IndentedStudentSolution.append(line)
                                    print("Index: ", index)
                                studentSolution = IndentedStudentSolution
                                
                                studentSolution = ""
                                studentSolution = studentSolution.join(IndentedStudentSolution)
                                print("stdentSol post join", studentSolution)
                                
                                
                                #apply newlines so the code will be formattedproperly
                                studentSolution = re.sub(r"§", "\n", studentSolution)
                                studentSolution = re.sub(r"ℊ ","\n", studentSolution)
                                
                                print("Student Solution", studentSolution);
                                question['student_solution'] = studentSolution
                                
                                studentSolution = 'IndentationArray:'+ str(lineIndent)+ ";" +studentSolution
                                
                                ##if no errors happened give them full credit
                                if(errorDescriptions == ""):
                                    
                                    print("Errors:", studentAnswerList)
                                    question['user_points'] = question['total_points']
                                
                                    studentAnswerList.append(studentSolution) 
                                ##otherwise grade on our criteria    
                                else:
                                    
                                    print("Student Solution Indented: ", studentSolution)
                                    studentAnswerList.append(studentSolution)
                                    
                                    
                                   
                                    indentationErrorCount = len(re.findall(r'(?=i.e. indentation)', repr(studentSolution)))
                                    
                                    ##grading section
                                    studentGrade = question['total_points']
                                    maxPoints = question['total_points']
                                    penalties = Decimal(0.0)
                                    
                                     ##if there was an indentation problem
                                    if indentation == "true":
                                        if indentationErrorCount > 0:
                                            ##we multiply by 1/2 because each wrong is half of 1/n
                                            penalties += (indentationErrorCount/correctLineCount)*(1/2)
                                    
                                    ##too few
                                    if(correctLineCount > studentSolutionLineCount):
                                        penalties += Decimal((correctLineCount - studentSolutionLineCount)*(1/correctLineCount))
                                        print("Penalties too few!: ", penalties)
                                        ##too many
                                    if(correctLineCount < studentSolutionLineCount):
                                        penalties += Decimal((studentSolutionLineCount - correctLineCount)*(1/correctLineCount))
                                        print("Penalties too many!: ", penalties)
                                        
                                    if wrongPositionLineNumberbers:
                                        wrongPositionLineNumberbers = [x.strip() for x in wrongPositionLineNumberbers.split(',')]
                                        print("WrongLineNumber length:", len(wrongPositionLineNumberbers))
                                        penalties += Decimal(len(wrongPositionLineNumberbers)/correctLineCount)
                                        print("WrongLine Number penalties: ", penalties) 
                                    if feedBackButtonClickCount > 0:
                                        maxPoints /=  feedBackButtonClickCount * 2
                                        print("Feedback button click count:" , feedBackButtonClickCount)
                                        print("Penalties after feedback:", penalties)
                                    
                                    #max poitns is all the maximum student points, and we subtract the penalties    
                                    studentGrade = maxPoints - maxPoints * penalties
                                    if studentGrade < 0:
                                            studentGrade = 0;
                                    
                                    print("Student grade:", studentGrade)
                                    print("Total Points:", question['total_points'])
                                    if(float(studentGrade) == float(question['total_points'])):
                                        question['user_points'] = question['total_points']
                                        print("Correct answer full points", question['user_points'])
                                    else:
                                        question['user_points'] = round(Decimal(studentGrade),2)
                            print("Final User Grade: ", question['user_points'])
                    totalStudentScore += question['user_points']
                    totalPossibleScore += question['total_points']            
                    if 'seed' in question:
                        seed = question['seed']
                    else:
                        seed = 0
                    studentChallengeQuestion = saveChallengeQuestion(studentChallenge, question['question']['questionID'], question['user_points'], question['total_points'], "",seed)

                    # Award skills if the answer was correct.
                    if question['user_points'] == question['total_points']:
                        saveSkillPoints(question['id'], currentCourse, studentId, studentChallengeQuestion)

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
                studentChallenge.save()
                
                if challenge.totalScore != totalPossibleScore:  # In case things have been changed since the last time it was taken or this is first time anyone has taken
                    challenge.totalScore = totalPossibleScore
                    challenge.save()
                
                register_event(Event.endChallenge,request,studentId,challengeId)
                register_event(Event.leaderboardUpdate,request,studentId, challengeId)
                updateLeaderboard(course)
                
                print("studentChallege ", studentChallenge)
                print("studentId ", studentId)
                
        if request.GET:      
            
            if 'warmUp' in request.GET:
                context_dict['warmUp'] = True
            if 'all' in request.GET:
                context_dict['all'] = True
            if 'classAchievements' in request.GET:
                context_dict['classAchievements'] = True
            if 'view' in request.GET:
                context_dict['view'] = True
                
            if 'studentChallengeID' in request.GET:
                studentChallengeId = request.GET['studentChallengeID']
                context_dict['studentChallengeID'] = request.GET['studentChallengeID']
            else:
                student = context_dict['student']
                challenge = Challenges.objects.get(pk=int(request.GET['challengeID']))
                studentChallengeId = StudentChallenges.objects.filter(studentID=student, courseID=currentCourse,challengeID=challenge.challengeID)
                
                        
            challengeId = request.GET['challengeID']
            challenge = Challenges.objects.get(pk=int(challengeId))
            context_dict['challengeName'] = challenge.challengeName
            context_dict['challengeID'] = request.GET['challengeID']
                        
            # Get all the questions for this challenge (AH)
            questionObjects= []
            challengeQuestions = []
            challenge_questions = StudentChallengeQuestions.objects.filter(studentChallengeID=studentChallengeId)
            for challenge_question in challenge_questions:
                questionObjects.append(challenge_question.questionID)
                challengeQuestions.append(challenge_question)
            
            # Find the total student score for this challenge attemmpt (AH)
            studentChallenges = StudentChallenges.objects.filter( courseID=currentCourse,challengeID=challengeId, studentChallengeID = studentChallengeId )
            for Schallenges in studentChallenges:
                if int(Schallenges.challengeID.challengeID) == int(challengeId):
                    totalStudentScore = Schallenges.testScore
            context_dict['total_user_points'] = totalStudentScore
                    
            # Next few lines of code is very similar to POST (AH)
            questions = []
            for i, challenge_question in zip(range(0,len(questionObjects)), challengeQuestions):
                q = questionObjects[i]

                questSessionDict = {}
                questSessionDict['id']=q.questionID
                questSessionDict['index']=i+1
                questSessionDict['total_points']=challenge_questions.get(questionID=q).questionTotal
                
                questdict = makeSerializableCopyOfDjangoObjectDictionary(q)
                    
                questdict.pop("_state",None)
                
                studentAnswers = StudentChallengeAnswers.objects.filter(studentChallengeQuestionID=challenge_question) 
                
                if q.type in staticQuestionTypesSet:
                    answers = [makeSerializableCopyOfDjangoObjectDictionary(ans) for ans in Answers.objects.filter(questionID = q.questionID)]
                    
                    answer_range = range(1,len(answers)+1)
                    questdict['answers_with_count'] = list(zip(answer_range,answers)) # answer_range is used for matching answers on the front-end (AH)
                    questSessionDict['answers'] = answers
                    questSessionDict['answers_with_count'] = questdict['answers_with_count']
                    
                    staticQuestion = StaticQuestions.objects.get(pk=q.questionID)
                    questdict['questionText']=staticQuestion.questionText
                    
                    #getting the matching questions of the challenge from database
                    matchlist = []
                    for match in MatchingAnswers.objects.filter(questionID=q.questionID):
                        matchdict = makeSerializableCopyOfDjangoObjectDictionary(match)
                        matchdict['answers_count'] = list(range(1,len(answers)+1))
                        matchdict['answerText'] = match.answerID.answerText
                        matchlist.append(matchdict)
                        
                    questSessionDict['matches']=[]
                    j = 1
                    for matchdict in matchlist:
                        questSessionDict['matches'].append(matchdict)
                        matchdict['current_pos'] = j
                        j = j + 1

                    questdict['matches']=matchlist
                    if q.type == QuestionTypes.parsons:
                        answer = Answers.objects.filter(questionID=q.questionID)
                        answer = answer[0].answerText
                        print("Model Solution: ", answer)
                        
                        #get the language information and indentation status
                        #remove the first line that keeps the data
                        searchString = re.search(r'Language:([^;]+);Indentation:([^;]+);', answer)
                        answer =  re.sub("##", "", answer)
                        indentation = searchString.group(2)
                        answer = answer.replace(searchString.group(0), "")
                        
                        
                        
                        answer =  re.sub("^ *\\t", "  ", answer)
        
                        #tokenizer characters ☃ and ¬
                        answer = re.sub("\n", "\n¬☃", answer)
                        answer = re.sub("^[ ]+?", "☃", answer)
                        
                        #we turn the student solution into a list
                        answer = [x.strip() for x in answer.split('¬')]
                        
                        #get how many spces there are in the first line
                        answer[0] = re.sub("☃"," ",answer[0])
                        leadingSpacesCount = len(answer[0]) - len(answer[0].lstrip(' '))
                        
                        #give each string the new line
                        tabedanswer = []
                        for index, line in enumerate(answer):
                            line = re.sub("☃", "", line)
                            line = re.sub(".*#distractor", "", line)
                            line = re.sub("^[ ]{" + str(leadingSpacesCount) + "}", "", line)
                            if index < len(answer)- 1:
                                line = line +"\n"
                            tabedanswer.append(line)
                        
                        answer = ""
                        answer = answer.join(tabedanswer)
                                                    
                        questSessionDict['model_solution'] = answer
                        
                        
                        studentAnswer = studentAnswers[0].studentAnswer
                        lineIndentRegex = re.search(r'IndentationArray:([^;]+);', studentAnswer)
                        if(lineIndentRegex != None):
                            lineIndent = lineIndentRegex.group(1)
                            studentAnswer = studentAnswer.replace(lineIndentRegex.group(0), "")
                            
                        else:
                            lineIndent = '[' + '0,' * 15 +'0]'
                        
                        
                        lineIndent = re.findall('\d+',lineIndent)    
                        
                        #we turn the student solution into a list
                        studentAnswer = [x.strip() for x in studentAnswer.split(',')]
                        #make a list of lines, split on , so we know how much to indent where
                        lineIndent = [int(line) for line in lineIndent]
                       
                        #perform the spacing for each line
                        IndentedStudentSolution = [];
                        for index, line in enumerate(studentAnswer,0):
                            line = '    ' * lineIndent[index] + line +'\n'
                            IndentedStudentSolution.append(line)
                        
                        studentAnswer = ""
                        studentAnswer = studentAnswer.join(IndentedStudentSolution)
                        
                        questSessionDict['student_solution'] = studentAnswer
                    
                    if q.type == QuestionTypes.multipleChoice:
                        correctAnswer = CorrectAnswers.objects.get(questionID=q.questionID).answerID
                        correctAnswerText = correctAnswer.answerText
                        questSessionDict['correct_answer_text'] = correctAnswerText
                        studentAnswerValue = studentAnswers[0].studentAnswer
                        userSelection = 0
                        userAnswer = {}
                        # Loop through to find the student answer (AH)
                        for index, answer in questdict['answers_with_count']:
                            if answer['answerID'] == int(studentAnswerValue):
                                userSelection = index
                                userAnswer = answer
                                break
                        # answerNumber is used to match answer choices on the front-end (AH)
                        questSessionDict['user_answer'] = {'answerNumber':userSelection,'answerText':userAnswer['answerText']}
                        
                        # Check to see if the student answer matches the correct answer (AH)
                        if int(studentAnswerValue) == correctAnswer.answerID:
                            questSessionDict['user_points'] = questSessionDict['total_points']
                        else:
                            questSessionDict['user_points'] = 0
                    elif q.type == QuestionTypes.multipleAnswers:
                        correctAnswers = [x.answerID for x in CorrectAnswers.objects.filter(questionID=q.questionID)]
                        correctAnswerIds = [x.answerID for x in correctAnswers]
                        questSessionDict['correct_answer_texts'] = [x.answerText for x in correctAnswers]
                        
                        # Finding the student answers (AH)
                        userAnswerIndexes = []
                        userAnswers = []
                        for stuAns in studentAnswers:
                            for index, answer in questdict['answers_with_count']:
                                if answer['answerID'] == int(stuAns.studentAnswer):
                                    userAnswerIndexes.append(index)
                                    userAnswers.append((index, answer))
                                    break
                        
                        userAnswerIndexes = [int(x) for x in userAnswerIndexes]   
                        userAnswerIds = [x['answerID'] for i, x in userAnswers]
                        
                        numAnswersIncorrect = len([x for x in userAnswerIds if x not in correctAnswerIds])                            
                        numAnswersMissing = len([x for x in correctAnswerIds if x not in userAnswerIds])
                            
                        valuePerAnswer = questSessionDict['total_points']/len(questSessionDict['answers'])
                        
                        questSessionDict['user_points'] = round(questSessionDict['total_points']-valuePerAnswer*(numAnswersIncorrect+numAnswersMissing), 2)
                        questSessionDict['user_answers'] = [{'answerNumber':i,'answerText':x['answerText']} for i, x in userAnswers]
                    elif q.type == QuestionTypes.trueFalse:
                        correctAnswerValue = CorrectAnswers.objects.get(questionID=q.questionID).answerID.answerText == "true"
                        
                        questSessionDict['correctAnswerText'] = str(correctAnswerValue)
                        
                        studentAnswerValue = studentAnswers[0].studentAnswer
                        questSessionDict['user_answer'] = {'answerText':str(studentAnswerValue),'answerValue':(studentAnswers[0].studentAnswer == 'True')}
                        if studentAnswerValue == str(correctAnswerValue):
                            questSessionDict['user_points'] = questSessionDict['total_points']
                        else:
                            questSessionDict['user_points'] = 0
                    elif q.type == QuestionTypes.matching:
                        userAnswers = []
                        userScore = []
                        matches = questdict['matches']
                        valuePerAnswer = questSessionDict['total_points']/len(questSessionDict['answers'])
                        userScore = 0
                        for match in matches:
                            if match is not None:
                                # Find correct answer
                                correctAnswerIndex = 0
                                for index,answer in questdict['answers_with_count']:
                                    if answer['answerID'] == match['answerID_id']:
                                        correctAnswerIndex = index
                                        break
                                    
                                # Find student answer that matches with the current match object (AH)
                                for stuAns in studentAnswers:
                                    userAnswerIndex = 0
                                    matchAnswer = stuAns.studentAnswer
                                    parts = matchAnswer.split(':')
                                
                                    for index,answer in questdict['answers_with_count']:
                                        if answer['answerID'] == int(parts[1]) and match['matchingAnswerID'] == int(parts[0]):
                                            userAnswerIndex = index
                                            break
                                    if userAnswerIndex != 0:
                                        break
                                userAnswers.append({'answerNumber':userAnswerIndex,'answerText':MatchingAnswers.objects.get(pk=parts[0]).answerID.answerText})
                                if correctAnswerIndex == userAnswerIndex:
                                    userScore = userScore + valuePerAnswer

                        questSessionDict['user_points'] = userScore
                        questSessionDict['user_answers'] = userAnswers
                elif q.type in dynamicQuestionTypesSet:
                    dynamicQuestion = DynamicQuestions.objects.get(pk=q.questionID)
                    if not lupa_available:
                        questdict['questionText'] = "<B>Lupa not installed.  Please ask your server administrator to install it to enable dynamic problems.</B>"
                    else:
                        if dynamicQuestion.numParts == 1:
                            seed = challenge_question.seed
                            questSessionDict['seed'] = seed
                            
                            code = [CodeSegment.new(CodeSegment.raw_lua,dynamicQuestion.code,"")]
                            numParts = dynamicQuestion.numParts
                            libs = makeLibs(dynamicQuestion)
                            lupaQuest = LupaQuestion(code, libs, seed, "dummy_uniqid", numParts)
    
                            questdict['questionText'] = lupaQuest.getQuestionPart(1)
                            answers = {}
                            for ans in studentAnswers:
                                answerParts = ans.studentAnswer.split(":") 
                                answers[answerParts[0]] = answerParts[1]
                            print(studentAnswers)
                            questSessionDict['user_answers'] = answers
                            questSessionDict['evaluations'] = lupaQuest.answerQuestionPart(1, answers)
                            if questSessionDict['evaluations']:
                                questSessionDict['user_points'] = sum([eval['value'] for eval in questSessionDict['evaluations']])
                            else:
                                questSessionDict['user_points'] = 0
                        else:
                            questSessionDict['user_points'] = 0
                    
                   
                questSessionDict['question']=questdict
                questions.append(questSessionDict)
                
                
            
            context_dict["questionCount"] = len(questions)
            context_dict['total_possible_points'] = sum([question['total_points'] for question in questions])

            # The sort on the next line should be unnecessary, but better safe than sorry
            context_dict['questions'] = sorted(questions,key=lambda q:q['index'])
            
    return render(request,'Students/ChallengeResults.html', context_dict)

