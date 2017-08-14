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
                
                register_event(Event.endChallenge,request,studentId,challengeId)

                return render(request,'Students/ChallengeResults.html', context_dict)


#-------------------------------------------------------------------------------------------
                for challenge_question in challenge_questions:
                    q_ID.append(challenge_question.questionID.questionID)
                    questionObjects.append(challenge_question.questionID)
                    
                    multiple_user = []
                    match_user = []
                    match_answer = []
                    match_question = []

                    #if the user has not answered a question and left it blank, except the matching question which has default values in the dropdowns as 1
                    if (str(challenge_question.questionID.questionID) in request.POST and request.POST[str(challenge_question.questionID.questionID)] != '') or (str(challenge_question.questionID.type) == '3'):
                       
                        # If it is a multiple answers or a matching question the answers must be saved in an array
                        if challenge_question.questionID.type == QuestionTypes.multipleAnswers:
                            #print("multiple answers:"+str(request.POST[str(challenge_question.questionID.questionID)]))
                            multiple_user = request.POST.getlist(str(challenge_question.questionID.questionID))
                            print("ma:"+str(multiple_user))
                            #useranswerObjects.append(multiple_user)
                            user_dict[challenge_question.questionID.questionID] = multiple_user
                            
                        # If it is a matching question the answers must be saved in an array
                        elif challenge_question.questionID.type == QuestionTypes.matching:
                            match_user = request.POST.getlist(str(challenge_question.questionID.questionID))
                            user_dict[challenge_question.questionID.questionID] = match_user
                            number_length = len(match_user) #what if user puts 2 same numbers beside the answers
                            #print("matching length:"+str(number_length))
                            
                            # Insert the user match answers into a new list basing on the numbers that he numbered beside the answers     
                            for j in range(0,number_length):
                                #inserting the match answers in same order as they were shuffled to display in the test taking page
                                match_question.append(request.POST[str(challenge_question.questionID.questionID)+'a-'+str(j+1)])
                                #added an if clause to make sure that the string whose index is required exists otherwise it returns an error.. also check the number of occurances of one string
                                if match_user.count(str(j+1)) == 1 and str(j+1) in match_user:
                                    #print("user numbers order:"+str(match_user[j]))
                                    index = match_user.index(str(j+1))
                                    match_answer.insert(j, request.POST[str(challenge_question.questionID.questionID)+'a-'+str(index+1)]) #placing the answer sting in the order that the user has numbered them
                                else:
                                    match_answer.insert(number_length-1, 'Used same number multiple times')# if user has assigned same number to 2 or more answers, then those answers shall be replaced by this string and inserted in the array
                             
                            #user_dict[challenge_question.questionID.questionID] = match_answer
                            match_question_dict[challenge_question.questionID.questionID] = match_question
                            match_sorted[challenge_question.questionID.questionID] = match_answer
                            
                        
                        else:
                            #print("answers:"+str(request.POST[str(challenge_question.questionID.questionID)]))
                            #useranswerObjects.append(request.POST[str(challenge_question.questionID.questionID)])
                            user_dict[challenge_question.questionID.questionID] = request.POST[str(challenge_question.questionID.questionID)]
                    else:
                        # If user has not answered the question, a default string is saved into the dictionary
                        user_dict[challenge_question.questionID.questionID] = "No Answer"
                        
                for cquest in challenge_questions:
                    questionId = cquest.questionID.questionID
                    print("questionID: "+str(questionId))
                    useranswerObjects.append(user_dict.get(questionId)) #For the display purpose in the html page, the user answers are being arranged in the order of question ids from database 
                    matchquestionObjects.append(match_question_dict.get(questionId))
                #print("Sorted user answers:"+str(useranswerObjects))
                #print("user part:"+str(user_dict))
                
            
                #Scoring
                for c_ques in challenge_questions:
                    
                    for key, value in user_dict.items():
                        if str(key) == str(c_ques.questionID.questionID):
                            if c_ques.questionID.type == QuestionTypes.multipleAnswers:
                                total = total + c_ques.points
                                answer = CorrectAnswers.objects.filter(questionID = key)
                                #print("key:"+str(key))
                                ma_point=0
                                #a=0
                                for ans in answer:          
                                    #if a <= (len(value))-1: 
                                        if str(ans.answerID.answerText) in value: # checking if the answers of the question are present in the array of the user answers for this question
                                            ma_point = ma_point+(c_ques.points/len(answer)) # here the total no. of answers must be awarded points but not for individual answer, so diving the total points awarder to the question with no. of answers
                                            print("score in ma is:"+str(ma_point))
                                            #a=a+1
                                if len(value)>len(answer): # if user has opted for more no. of answers that the no. of correct answers, the point for this question must be deducted. If the points are less than 0, a zero is awarded
                                    ma_point = ma_point-(((len(value)-len(answer))*c_ques.points)/len(answer))
                                    print("score in more ma final:"+str(ma_point))
                                    if ma_point<0:
                                        ma_point=0
                                        
                                #save student's challenge-question information pair to db 
                                studentChallengeQuestion = saveChallengeQuestion(studentChallenge, key, ma_point, c_ques.points, instructorFeedback)       
                                
                                questionScore_dict[key] = ma_point
                                questionTotal_dict[key] = c_ques.points
                                
                                #save student's challenge-question-answer information pair to db
                                for ma_answer in value:
                                    studentChallengeAnswers = StudentChallengeAnswers()
                                    studentChallengeAnswers.studentChallengeQuestionID = studentChallengeQuestion
                                    studentChallengeAnswers.studentAnswer = ma_answer
                                    studentChallengeAnswers.save()
                                
                                score=score+ma_point
                                
                                if c_ques.points == ma_point: #adding skill points
                                    saveSkillPoints(c_ques.questionID.questionID, challengeId, studentId, studentChallengeQuestion)
    
                            elif str(c_ques.questionID.type) == QuestionTypes.matching:
                                for match_key,match_value in match_sorted.items():
                                    if str(key) == str(match_key):
                                        a=0
                                        match_point=0
                                        total = total + c_ques.points
                                        match_ans = MatchingAnswers.objects.filter(questionID = key)
                                        for matches in match_ans:
                                            if str(matches.matchingAnswerText) == str(match_value[a]): #since the correct answers are ordered, we just check the order of user answers array for this question as we have already sorted them in the order that user has numbered. So, if the order is correct then answer is correct
                                                match_point = match_point+(c_ques.points/len(match_ans))
                                                print("match:"+str(match_point))
                                            a=a+1
                                            
                                        #save student's challenge-question information pair to db 
                                        studentChallengeQuestion = saveChallengeQuestion(studentChallenge, key, match_point, c_ques.points, instructorFeedback)   
                                        
                                        questionScore_dict[key] = match_point
                                        questionTotal_dict[key] = c_ques.points
                                        
                                        #save student's challenge-question-answer information pair to db
                                        for match_answer in value: #match_value
                                            studentChallengeAnswers = StudentChallengeAnswers()
                                            studentChallengeAnswers.studentChallengeQuestionID = studentChallengeQuestion
                                            studentChallengeAnswers.studentAnswer = match_answer
                                            studentChallengeAnswers.save()
                                            
                                        score = score+match_point
                                        print("score after match:"+str(score))
                                        
                                        if c_ques.points == match_point: #adding skill points
                                            saveSkillPoints(c_ques.questionID.questionID, challengeId, studentId, studentChallengeQuestion)
                                         
                                # inserting the shuffled order of the matching right hand side answers into database for displaying purpose 
                                for matchQues_key,matchQues_value in match_question_dict.items():
                                    if str(key) == str(matchQues_key):
                                        print("match_value:"+str(matchQues_value))
                                        for i in range(0,len(matchQues_value)):
                                            matchShuffledAnswers = MatchShuffledAnswers()
                                            matchShuffledAnswers.studentChallengeQuestionID = studentChallengeQuestion
                                            print("inserting:"+str(matchQues_value[i]))
                                            matchShuffledAnswers.MatchShuffledAnswerText = matchQues_value[i]
                                            matchShuffledAnswers.save()
                                           
                                       
                                    
                            elif str(c_ques.questionID.type) == QuestionTypes.essay:
                                
                                total = total + c_ques.points # since there is no correct answer in database, a 0 is awarded for this question. The score to these questions shall be awarded by the instructor
                                #save student's challenge-question information pair to db
                                # questionScore initially is zero and updated after Instructor's evaluation
                                studentChallengeQuestion = saveChallengeQuestion(studentChallenge, key, 0, c_ques.points, instructorFeedback)

                                questionScore_dict[key] = 0
                                questionTotal_dict[key] = c_ques.points 
                                
                                #save student's challenge-question-answer information pair to db
                                studentChallengeAnswers = StudentChallengeAnswers()
                                studentChallengeAnswers.studentChallengeQuestionID = studentChallengeQuestion
                                studentChallengeAnswers.studentAnswer = value
                                studentChallengeAnswers.save()
                                
#                                 if c_ques.points == ma_point: #It is an essay question, so skill points cannot be automatically added
                                        
                            else:
                                answer = CorrectAnswers.objects.filter(questionID = key)     
                                point=0
                                total = total + c_ques.points
                                for ans in answer:
                                    if str(value).lower() == str(ans.answerID.answerText).lower():
                                        
                                        point = c_ques.points
                                        
                                #save student's challenge-question information pair to db
                                studentChallengeQuestion = saveChallengeQuestion(studentChallenge, key, 0, point, instructorFeedback)
                                        
                                questionScore_dict[key] = point
                                questionTotal_dict[key] = c_ques.points
                                        
                                #save student's challenge-question-answer information pair to db
                                studentChallengeAnswers = StudentChallengeAnswers()
                                studentChallengeAnswers.studentChallengeQuestionID = studentChallengeQuestion
                                studentChallengeAnswers.studentAnswer = value
                                studentChallengeAnswers.save()
                                        
                                score = score+point
                                if c_ques.points == point: #adding skill points
                                    saveSkillPoints(c_ques.questionID.questionID, challengeId, studentId, studentChallengeQuestion)                
                
                studentChallenge.testScore = score
                studentChallenge.testTotal = total
                studentChallenge.save()
                            
                score_list.append(score)
                total_list.append(total)
                
                qlist = []
                for q in questionObjects:
                    questdict = q.__dict__
                    correct_answers = CorrectAnswers.objects.filter(questionID = q.questionID)
                    canswer_range = range(1,len(correct_answers)+1)
                    questdict['correct_answers'] = zip(canswer_range,correct_answers)
                    
                    #questdict['user_answers'] = useranswerObjects
                    
                    answers = Answers.objects.filter(questionID = q.questionID)
                    answer_range = range(1,len(answers)+1)
                    questdict['answers_with_count'] = zip(answer_range,answers)
                    questdict['match_with_count'] = zip(answer_range,answers)
                    #questdict['match_shuffled'] = matchquestionObjects
                                        
                    questionId = q.questionID
                    questionScore_list.append(questionScore_dict.get(questionId))
                    questionTotal_list.append(questionTotal_dict.get(questionId))

                    staticQuestion = StaticQuestions.objects.get(pk=questionId)
                    questdict['questionText']=staticQuestion.questionText                       
                    questdict['typeID']=str(q.type)
                    questdict['challengeID']= challengeId
                                        
                    matchlist = []
                    for match in MatchingAnswers.objects.filter(questionID=q.questionID):
                        matchdict = match.__dict__
                        matchdict['answers_count'] = range(1,int(len(answers))+1)
                        matchlist.append(matchdict)
                    questdict['matches']=matchlist
                    qlist.append(questdict)            
                
                #Register timePassed event indicating that the time limit for a challenge has been reached
                #submit_hidden indicates that the time limit for the challenge has been reached
                if 'submit_hidden' in request.POST:
                    register_event(Event.timePassed, request, studentId, challengeId)
                    print("Registered Event: Time Passed Event, Student: " + str(studentId) + ", Challenge: " + str(challengeId))

                            
            register_event(Event.endChallenge,request,studentId,challengeId)
            print("Registered Event: End Challenge Event, Student: " + str(studentId) + ", Challenge: " + str(challengeId))
            
            # The range part is the index numbers.     
            context_dict['question_range'] = zip(range(1,len(questionObjects)+1),qlist,useranswerObjects,matchquestionObjects,questionScore_list,questionTotal_list)
            context_dict['score_range'] = score_list
            context_dict['total_range'] = total_list
    
    return render(request,'Students/ChallengeResults.html', context_dict)

