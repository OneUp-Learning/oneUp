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

def makeSerializableCopyOfDjangoObjectDictionary(obj):
    dict = obj.__dict__.copy()
    # We remove the Django Status object from the dictionary to prevent serialization problems
    dict.pop("_state",None)
    return dict

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
                    questionObjects.append(challenge_question.questionID)
                
                #getting all the question of the challenge except the matching question
                qlist = []
                sessionDict['questions'] = []
                for i in range(0,len(questionObjects)):
                    q = questionObjects[i]

                    questSessionDict = {}
                    questSessionDict['index']=i+1
                    questSessionDict['total_points']=challenge_questions.get(questionID=q).points
                    
                    questdict = makeSerializableCopyOfDjangoObjectDictionary(q)
                    
                    questdict.pop("_state",None)
                                        
                    if q.type in staticQuestionTypesSet:
                        answers = [makeSerializableCopyOfDjangoObjectDictionary(ans) for ans in Answers.objects.filter(questionID = q.questionID)]
                        if q.type != QuestionTypes.trueFalse:
                            random.shuffle(answers)
                        answer_range = range(1,len(answers)+1)
                        questdict['answers_with_count'] = list(zip(answer_range,answers))

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
                        
                        random.shuffle(matchlist)
    
                        questSessionDict['matches']=[]
    
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
                            questSessionDict['lupaquestion'] = lupaQuest.serialize()
                            questdict['requestType'] = '_eval';
                            if numParts > 1:
                                questdict['hasMultipleParts'] = True
                                questSessionDict['hasMultipleParts'] = True
                            else:
                                questdict['hasMultipleParts'] = False
                                questSessionDict['hasMultipleParts'] = False
                       
                    qlist.append(questdict)
                    questSessionDict['question']=questdict
                    sessionDict['questions'].append(questSessionDict)

            request.session[attemptId]=sessionDict
            print("attemptID = "+attemptId)               
            context_dict['question_range'] = zip(range(1,len(questionObjects)+1),qlist)
            
        register_event(Event.startChallenge,request,None,challengeId)
        print("Registered Event: Start Challenge Event, Student: student in the request, Challenge: " + challengeId)
        
    return render(request,'Students/ChallengeSetup.html', context_dict)

