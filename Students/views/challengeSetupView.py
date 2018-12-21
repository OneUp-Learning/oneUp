from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import random 
from datetime import datetime
import sys

##GMM import Regular Expression, re
import re,string

from Instructors.models import Challenges, Answers, DynamicQuestions, Questions
from Instructors.models import ChallengesQuestions, MatchingAnswers, StaticQuestions
from Students.models import DuelChallenges
from Instructors.views.utils import utcDate
from Students.views.utils import studentInitialContextDict
from Badges.events import register_event
from Badges.enums import Event, staticQuestionTypesSet, dynamicQuestionTypesSet,\
    QuestionTypes
from Instructors.lupaQuestion import lupa_available, LupaQuestion, CodeSegment
from Instructors.views.dynamicQuestionView import makeLibs
from locale import currency
from django.db.models.functions.window import Lead

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
        sessionDict = {}  
        attemptId=''      
        if request.POST:        
            if request.POST['challengeId']: 
                
                context_dict['questionTypes']= QuestionTypes
                
                challengeId = request.POST['challengeId']
                context_dict['challengeID']= challengeId
                challenge = Challenges.objects.get(pk=int(request.POST['challengeId']))

                if "duelID" in request.POST:
                    duel_id = request.POST['duelID']
                    duel_challenge = DuelChallenges.objects.get(pk=int(duel_id))
                    context_dict['challengeName'] = duel_challenge.duelChallengeName
                    context_dict['isduration'] = True
                    context_dict['testDuration'] = duel_challenge.timeLimit
                    context_dict['isDuel'] = True
                    context_dict['duelID'] = duel_id
                else:
                    context_dict['challengeName'] = challenge.challengeName
                    if challenge.timeLimit == 99999:
                        context_dict['isduration'] = False
                    else:
                        context_dict['isduration'] = True
                    context_dict['testDuration'] = challenge.timeLimit
                    context_dict['isDuel'] = False

                starttime = utcDate()
                context_dict['startTime'] = starttime.strftime("%m/%d/%Y %I:%M:%S %p")
                attemptId = 'challenge:'+challengeId + '@' + starttime.strftime("%m/%d/%Y %I:%M:%S %p")
                
                sessionDict['challengeId']=challengeId
                
                if not challenge.isGraded:
                    context_dict['warmUp'] = 1
                       
                # Checks if password was entered correctly
                if challenge.challengePassword != '':
                    if 'password' not in request.POST or request.POST['password'] != challenge.challengePassword:
                        return redirect('/oneUp/students/ChallengeDescription?challengeID=' + challengeId)

#                 if challenge.challengeName == "Parsons":
#                     context_dict['questionType'] = 'parsons'
#                     context_dict['questionText'] = "Construct a function by drag&amp;dropping and reordering lines from the left to the right.The constructed function should return True if the parameter is True and return False otherwise."
#                     return render(request,'Students/ChallengeSetup.html', context_dict)
                
                #GGM changed it so that it will now order by the question position
                #this allows us to easily order by randomization in the future
                currentChallenge = Challenges.objects.filter(challengeID=challengeId).first()
                isRandomized = currentChallenge.isRandomized
                
                if(isRandomized):
                    ##GGM this line is problematic for large data sets
                    challenge_questions = ChallengesQuestions.objects.filter(challengeID=challengeId).order_by('?')
                else:
                    challenge_questions = ChallengesQuestions.objects.filter(challengeID=challengeId).order_by("questionPosition")
                print("Challenge Questions", challenge_questions)
                for challenge_question in challenge_questions:
                    questionObjects.append(challenge_question.questionID)
                
                #getting all the question of the challenge except the matching question

                qlist = []
                sessionDict['questions'] = []
                for i in range(0,len(questionObjects)):
                    q = questionObjects[i]

                    questSessionDict = {}
                    questSessionDict['id']=q.questionID
                    questSessionDict['index']=i+1
                    questSessionDict['total_points']=challenge_questions.get(questionID=q).points
                    
                    questdict = makeSerializableCopyOfDjangoObjectDictionary(q)
                    
                    questdict.pop("_state",None)
                                        
                    if q.type in staticQuestionTypesSet:
                        answers = [makeSerializableCopyOfDjangoObjectDictionary(ans) for ans in Answers.objects.filter(questionID = q.questionID)]
                        if q.type != QuestionTypes.trueFalse and q.type != QuestionTypes.parsons:
                            random.shuffle(answers)
                        answer_range = range(1,len(answers)+1)
                        questdict['answers_with_count'] = list(zip(answer_range,answers))

                        questSessionDict['answers'] = answers
                        questSessionDict['answers_with_count'] = questdict['answers_with_count']
                        
                        staticQuestion = StaticQuestions.objects.get(pk=q.questionID)
                        questdict['questionText']=staticQuestion.questionText

                        # Parsons problems: getting the model solution from the database - it is saved in Answers.answerText
                        if q.type == QuestionTypes.parsons:
                            if not challenge.isGraded:
                                context_dict['warmUp'] = 1
                            else:
                                context_dict['warmUp'] = 0
                            modelSolution = Answers.objects.filter(questionID=q)
                            solution_string = modelSolution[0].answerText
                            
                            #dynamically set dfficulty of parson distractor
                            questionHardness = Questions.objects.filter(questionID=q.questionID)
                            questionDifficulty = questionHardness[0].difficulty
                            
        
                            questdict['languageName'] = re.search(r'Language:([^;]+)', solution_string).group(1).lower().lstrip()
                            questdict['indentation'] = re.search(r';Indentation:([^;]+);', solution_string).group(1)
                            
                            
                            languageAndLanguageName = re.search(r'Language:([^;]+)', solution_string)
                            intentationEnabledVariableAndValue = re.search(r';Indentation:([^;]+);', solution_string)
                            solution_string = solution_string.replace(languageAndLanguageName.group(0), "")
                            solution_string = solution_string.replace(intentationEnabledVariableAndValue.group(0), "")

                            
                            
                            #get the count of the distractors
                            
                            distractorCount = len(re.findall(r'(?=#dist)', repr(solution_string).strip('"\'')))
                            questdict['distractorCount'] = distractorCount
                            
                            
                            #set the count of distractors off the question's hardness
                            if(questionDifficulty == "Easy"):
                                distractorCount = 0
                            if(questionDifficulty == "Medium"):
                                distractorCount = int(distractorCount/2)
                                
                            questdict['distractorCount'] = distractorCount    
                            #if the question difficulty is hard, 
                            ##then we just use the full distractor count

                            
                            #repr function will give us the raw representation of the string
                            solution_string =  re.sub("\\r", "", solution_string)
                            solution_string =  re.sub("^ *\\t", "  ", solution_string)
                            solution_string =  re.sub("^\\t *", "  ", solution_string)
                            
                            #tokenizer characters ☃ and ¬
                            solution_string = re.sub("\n", "\n¬☃", solution_string)
                            solution_string = re.sub("^[ ]+?", "☃", solution_string)
                            print("Solution StringF", solution_string)
                            
                            #we turn the student solution into a list
                            solution_string = [x.strip() for x in solution_string.split('¬')]
                            print("solutionString", solution_string)
                            
                            #give each string the new line
                            tabedSolution_string = []
                            
                            #indentation flag allows checking to see if next line should be indented
                            indentationFlag = 0
                            pattern = re.compile("##")
                            for line in solution_string:
                                originalLine= line
                                #we need the original line to match against when we find the next element
                                line = re.sub("☃", "", line)
                                if(indentationFlag == 1):
                                    #if indentation flag is 1 then we know that on this line we must indent
                                    indentationFlag = 0
                                    line = re.sub("^ *", '&nbsp;'+ ' '* 4, line)
                                leadingSpacesCount = len(line) - len(line.lstrip(' '))
                                if(pattern.search(line) != None):
                                    #get the net line, find out its spaces count
                                    nextelem =solution_string[solution_string.index(originalLine) +1]
                                    nextelem = re.sub("☃", "", nextelem)
                                    leadingSpacesCountNextLine = len(nextelem) - len(nextelem.lstrip(' '))
                                    
                                    #we use the difference to calculate whether we must indent and where 
                                    difference = leadingSpacesCount - leadingSpacesCountNextLine
                                    print("Difference", difference)
                                    if(difference == -4):
                                        #if indentation is after the line
                                        #ex:
                                        #data++;
                                        #   index++;
                                        indentationFlag = 1
                                    if(difference == 4):
                                        #if indentation is before the line
                                        #ex:
                                        #   data++;
                                        #index++;
                                        modifier = int(leadingSpacesCount / 2)
                                        if(modifier > 1 and leadingSpacesCount == 8):
                                            #this modifier multiplies by the spaces count, if 8 then 4 in front, 4 after nbsp
                                            #this is a quirk of parsons.js
                                            line = re.sub("^ *", ' '* modifier + '&nbsp;'+ ' '* 5, line)
                                        else:
                                            line = re.sub("^ *", '&nbsp;'+ ' '* 4, line)
                                line = line +"\n"
                                tabedSolution_string.append(line)
                            

                            solution_string = ""
                            solution_string = solution_string.join(tabedSolution_string)
                            print("tabbedSol String", tabedSolution_string)
                            print("joinedSolString", solution_string)
                            
                            solution_string =  re.sub("##\\n *", "\\\\n", solution_string)
                            
                            
                            questdict['model_solution']=repr(solution_string).strip('\'')
                            print("questdict['model_solution']", questdict['model_solution'])
                                            
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
                            seed = random.randint(-2147483647,2147483646)
                            questSessionDict['seed'] = seed
                            
                            code = [CodeSegment.new(CodeSegment.raw_lua,dynamicQuestion.code,"")]
                            numParts = dynamicQuestion.numParts
                            libs = makeLibs(dynamicQuestion)
                            part = 1
                            lupaQuest = LupaQuestion(code, libs, seed, str(i+1), numParts)

#                            if (lupaQuest.error):
#                                context_dict['error']=lupaQuest.error
#                                return render(request,'Instructors/DynamicQuestionAJAXResult.html',context_dict)

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

