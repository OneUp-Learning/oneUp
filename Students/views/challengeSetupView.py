from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import random 
from time import strftime

from Instructors.models import Challenges, Answers, DynamicQuestions
from Instructors.models import ChallengesQuestions, MatchingAnswers, StaticQuestions
from Students.views.utils import studentInitialContextDict
from Badges.events import register_event
from Badges.enums import Event, staticQuestionTypesSet, dynamicQuestionTypesSet,\
    QuestionTypes
from Instructors.lupaQuestion import lupa_available, LupaQuestion, CodeSegment
from Instructors.views.dynamicQuestionView import makeLibs

@login_required
def ChallengeSetup(request):

    context_dict,currentCourse = studentInitialContextDict(request)                

    if 'currentCourseID' in request.session:    

        questionObjects= []
                
        if request.POST:        
            if request.POST['challengeId']: 
                
                context_dict['questionTypes']= QuestionTypes
                
                challengeId = request.POST['challengeId']
                context_dict['challengeID']= challengeId
                challenge = Challenges.objects.get(pk=int(request.POST['challengeId']))
                context_dict['challengeName'] = challenge.challengeName
                context_dict['testDuration'] = challenge.timeLimit

                starttime = strftime("%Y-%m-%d %H:%M:%S")
                context_dict['startTime'] = starttime 
                attemptId = 'challenge:'+challengeId + '@' + starttime
                
                sessionDict = {}
                sessionDict['challengeId']=challengeId
                
                if not challenge.isGraded:
                    context_dict['warmUp'] = 1
                       
                # Checks if password was entered correctly
                if challenge.challengePassword != '':
                    if 'password' not in request.POST or request.POST['password'] != challenge.challengePassword:
                        return redirect('/oneUp/students/ChallengeDescription?challengeID=' + challengeId)
                
                challenge_questions = ChallengesQuestions.objects.filter(challengeID=challengeId)
                for challenge_question in challenge_questions:
                    print("challenge_question.questionID: "+str(challenge_question.questionID))
                    questionObjects.append(challenge_question.questionID)
                
                #getting all the question of the challenge except the matching question
                qlist = []
                for i in range(0,len(questionObjects)):
                    q = questionObjects[i]

                    questSessionDict = {}
                    questSessionDict['question']=q
                    
                    questdict = q.__dict__.copy()
                                        
                    if q.type in staticQuestionTypesSet:
                        answers = list(Answers.objects.filter(questionID = q.questionID))
                        if q.type != QuestionTypes.trueFalse:
                            random.shuffle(answers)
                        answer_range = range(1,len(answers)+1)
                        questdict['answers_with_count'] = list(zip(answer_range,answers))

                        # We're setting up a list of the answers in the order they were given in the 
                        # session store.  When we grade this challenge, we will only know that they
                        # answered with answer number 1 or 2 or whatever.
                        # We start with [None] so that it will effectively be 1-indexed instead of 0-indexed
                        # since the answers are numbered that way.
                        questSessionDict['answers'] = [None]
                        for answer in answers:
                            questSessionDict['answers'].append(answer)
                        
                        staticQuestion = StaticQuestions.objects.get(pk=q.questionID)
                        questdict['questionText']=staticQuestion.questionText
                        print('questionText = ' + staticQuestion.questionText)
                        print(questdict)
                    
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
    
                        # This is to store the order of the matching answers.
                        # The None is there as an initial space filler to be the 0 element.
                        questSessionDict['matches']=[None]
    
                        j = 1
                        for matchdict in matchlist:
                            questSessionDict['matches'].append(matchdict)
                            matchdict['current_pos'] = j
                            j = j + 1
    
                        questdict['matches']=matchlist
                    elif q.type in dynamicQuestionTypesSet:
                        dynamicQuestion = DynamicQuestions.objects.get(pk=q.questionID)
                        if not lupa_available:
                            questdict['questionText'] = "<B>Lupa not installed.  Please ask your server administrator to install it to enable dynamic problems.</B>"
                        else:
                            seed = random.random()
                            questSessionDict['seed'] = seed
                            
                            code = [CodeSegment.new(CodeSegment.raw_lua,dynamicQuestion.code,"")]
                            numParts = dynamicQuestion.numParts
                            libs = makeLibs(dynamicQuestion)
                            part = 1
                            lupaQuest = LupaQuestion(code, libs, seed, str(i+1), numParts)

                            if (lupaQuest.error):
                                context_dict['error']=lupaQuest.error
                                return render(request,'Instructors/DynamicQuestionAJAXResult.html',context_dict)

                            questdict['questionText'] = lupaQuest.getQuestionPart(1)
                            print("Dynamic Question part is: "+questdict['questionText'])
                            questSessionDict['lupaquestion'] = lupaQuest.serialize()
                            questdict['requestType'] = '_eval';
                            if numParts > 1:
                                questdict['hasMultipleParts'] = 'True';
                                                    
                    qlist.append(questdict)

            request.session[attemptId]=sessionDict                
            context_dict['question_range'] = zip(range(1,len(questionObjects)+1),qlist)
            
        register_event(Event.startChallenge,request,None,challengeId)
        print("Registered Event: Start Challenge Event, Student: student in the request, Challenge: " + challengeId)
        
    return render(request,'Students/ChallengeSetup.html', context_dict)

