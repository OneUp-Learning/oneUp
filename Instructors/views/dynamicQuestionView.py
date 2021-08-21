'''
Created on Apr 1, 2014

@author: irwink
'''

import os
from datetime import datetime
from decimal import Decimal

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render

from Badges.enums import ObjectTypes
from Instructors.constants import (unassigned_problems_challenge_name,
                                   unlimited_constant)
from Instructors.lupaQuestion import CodeSegment, LupaQuestion, lupa_available
from Instructors.models import (Challenges, ChallengesQuestions, Courses,
                                DynamicQuestions, QuestionLibrary)
from Instructors.questionTypes import QuestionTypes
from Instructors.views import utils
from Instructors.views.templateDynamicQuestionsView import (
    getAllLuaLibraryNames, getLibrariesForQuestion, makeDependentLibraries,
    templateToCodeSegments)
from Instructors.views.utils import extractTags, initialContextDict, saveTags, update_or_create_challenge_questions

from oneUp.ckeditorUtil import config_ck_editor
from oneUp.decorators import instructorsCheck
from oneUp.settings import BASE_DIR


@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')   
def dynamicQuestionForm(request):
    context_dict, currentCourse = initialContextDict(request)
    
    # In this view, these are the names of the attributes which are just passed through with no processing.
    # We put them in an array so that we can copy them from one item to
    # another programmatically instead of listing them out.
    passthrough_attributes = ['preview','difficulty',
                         'instructorNotes','code','numParts','author','submissionsAllowed','resubmissionPenalty'];

    context_dict['skills'] = utils.getCourseSkills(currentCourse)
    context_dict['tags'] = []
    if request.POST:

        # If there's an existing question, we wish to edit it.  If new question,
        # create a new Question object.
        if 'questionId' in request.POST:
            question = DynamicQuestions.objects.get(pk=int(request.POST['questionId']))
        else:
            question = DynamicQuestions()

        # Copy all strings from POST to database object.
        for attr in passthrough_attributes:
            setattr(question,attr,request.POST[attr])
        question.questionText = ""  
        
        # if user did not specify author of the question, the author will be the user
        if question.author == '':
            question.author = request.user.username
            
        question.save();  #Writes to database.
                 
        # Fix the question type
        question.type = QuestionTypes.dynamic
        question.save();  #Writes to database.
        
        if 'challengeID' in request.POST:
            # save in ChallengesQuestions if not already saved        # 02/28/2015    
            update_or_create_challenge_questions(request,question)

            # save question-skill pair to db                    # 03/01/2015
            # first need to check whether a new skill is selected 

            # Processing and saving tags in DB
            saveTags(request.POST['tags'], question, ObjectTypes.question)
            
            if request.session['currentCourseID']:          # we presume the course is selected!!!!!!!!!!!!!!!!!!!!!!!!!
                courseID = Courses.objects.get(pk=int(request.session['currentCourseID']))
                
                # Processing and saving skills for the question in DB
                utils.addSkillsToQuestion(currentCourse,question,request.POST.getlist('skills[]'),request.POST.getlist('skillPoints[]'))
            
            makeDependentLibraries(question,request.POST.getlist('dependentLuaLibraries[]'))
            
            redirectVar = redirect('/oneUp/instructors/challengeQuestionsList', context_dict)
            redirectVar['Location']+= '?challengeID='+request.POST['challengeID']
            return redirectVar
        # Question is unassigned so create unassigned challenge object
        challenge = Challenges()
        challenge.challengeName = unassigned_problems_challenge_name
        challenge.courseID = currentCourse
        challenge.numberAttempts = unlimited_constant
        challenge.timeLimit = unlimited_constant
        challenge.save()
        ChallengesQuestions.addQuestionToChallenge(question, challenge, 0, 0)
        
        redirectVar = redirect('/oneUp/instructors/challengeQuestionsList?problems', context_dict) 
        return redirectVar
    
    elif request.method == 'GET':
        if 'view' in request.GET:
            context_dict['view'] = request.GET['view']
        context_dict['lib_range'] = getAllLuaLibraryNames();
        if Challenges.objects.filter(challengeID = request.GET['challengeID'],challengeName=unassigned_problems_challenge_name):
            context_dict["unassign"]= 1
        
        if 'challengeQuestionID' in request.GET:
            context_dict['challengeQuestionID'] = request.GET['challengeQuestionID']

        if 'challengeID' in request.GET:
            context_dict['challengeID'] = request.GET['challengeID']
            chall = Challenges.objects.get(pk=int(request.GET['challengeID']))
            context_dict['challengeName'] = chall.challengeName
            context_dict['challenge'] = True
                
        # If questionId is specified then we load for editing.
        if 'questionId' in request.GET:
            question = DynamicQuestions.objects.get(pk=int(request.GET['questionId']))
            
            # Copy all of the attribute values into the context_dict to
            # display them on the page.
            context_dict['questionId']=request.GET['questionId']
            for attr in passthrough_attributes:
                context_dict[attr]=getattr(question,attr)
                
            context_dict['selectedLuaLibraries'] = getLibrariesForQuestion(question)

            # Extract the tags from DB
            context_dict['tags'] = extractTags(question, "question")

            if 'challengeID' in request.GET:
                # get the challenge points for this problem to display
                if 'challengeQuestionID' in request.GET:
                    challenge_questions = ChallengesQuestions.objects.filter(pk=int(request.GET['challengeQuestionID']))
                    context_dict['points'] = challenge_questions[0].points
                else:
                    context_dict['points'] = 0
                    
                # set default skill points - 1
                context_dict['q_skill_points'] = int('1')

                # Extract the skill                                        
                context_dict['selectedSkills'] = utils.getSkillsForQuestion(currentCourse,question) 

        else:
            code = '''\
part_1_text = function ()
    return 'What is 1+1?' .. make_input('answer1','number',10)
end
evaluate_answer_1 = function(answers)
    if (tonumber(answers.answer1)==2)
       then return {answer1={success=true,value=10}}
       else return {answer1={success=false,value=0}}      
    end
end
part_1_max_points = function()
    return {answer1=10}
end
'''
            context_dict["code"] = code
            context_dict["numParts"] = 1
            context_dict['difficulty']="Easy"
            context_dict['tags'] = []
    
    if 'questionId' in request.POST:         
            return redirect('challengesView')

    context_dict['ckeditor'] = config_ck_editor()
            
    return render(request,'Instructors/DynamicQuestionForm.html', context_dict)

def makePartHTMLwithForm(question,part):
    formID = question.uniqid+'-'+str(part)
    formHead = ('<form name="'+formID+'" id="'+formID+'" action="doDynamicQuestion" method="POST" onSubmit="copyAJAXEditorsToHidden(\''+
                formID+'\');submit_form(\''+
                question.uniqid+'\','+str(part)+',makeAllEditors);disableDiv(\''+question.uniqid+'-'+str(part)+'\');return false;" >')
    formBody = '<input type="hidden" name="_part" value="'+str(part+1)+'">'
    formBody += '<input type="hidden" name="_uniqid" value="'+question.uniqid+'">'
    if (int(part) <= question.numParts):
        questionpart = question.getQuestionPart(part)
        if questionpart != False:
            formBody += '<div class="input-field col s12">'
            formBody += questionpart
            formBody += '</div>'
    formBody += '<button class="btn waves-effect waves-light" type="submit" value="Submit" name="submit">Submit<i class="material-icons right">send</i></button></form>'
    return (formHead,formBody)

def makePartHTMLwithoutForm(question,part):
    qhtml = question.getQuestionPart(part)
    return qhtml

def dynamicQuestionGetPartNonAJAX():
    return ""

def makeLibs(dynamicQuestion):
    libs = QuestionLibrary.objects.filter(question=dynamicQuestion)
    return [lib.library.libraryName for lib in libs]

def rescale_evaluations(evals,scale):
    for evaluation in evals:
        evaluation['value'] *= scale
        if 'details' in evaluation:
            for detail in evaluation['details']:
                detail['value'] *= scale
                detail['max_points'] *= scale
    return evals

def calcResubmissionPenalty(subCount,qdict):
    ahundred = Decimal(100)
    return Decimal(max(ahundred - (Decimal(subCount) * Decimal(qdict["resubmissionPenalty"])),0)/ahundred)

def convertStringOrTenIfBlank(s,convertFun):
    if s == "":
        return convertFun(10)
    else:
        return convertFun(s)

@login_required
def dynamicQuestionPartAJAX(request):
    context_dict = {}
    if not lupa_available:
        context_dict['error_message'] = "<B>Lupa not installed.  Please ask your server administrator to install it to enable dynamic problems.</B>"
        return render(request,'Instructors/DynamicQuestionAJAXResult.html',context_dict)

    if request.method == 'POST':
        attemptId = request.POST['_attemptId']
        inChallenge = request.POST['_inChallenge']=="true"
        partNum = int(request.POST['_partNum'])
        inTryOut = request.POST['_inTryOut']=="true"
        errorInLupaQuestionConstructor = False
        if ('_inittestquestion' in request.POST):
            numParts = int(request.POST['_numParts'])
            if '_code' in request.POST:
                code = [CodeSegment.new(CodeSegment.raw_lua,request.POST['_code'],"")]
                dynamic_type = "raw_lua"
            else:
                templateParts = []
                templateMaxPoints = dict()
                for i in range(1,numParts+1):
                    templateParts.append(request.POST['_templateText'+str(i)])
                    templateMaxPoints[i]=int(request.POST['_partpoints'+str(i)])
                code = templateToCodeSegments(request.POST['_setupCode'],templateParts)
                dynamic_type = "template"
            seed = request.POST['_seed']
            libs = request.POST.getlist('_dependentLuaLibraries[]')
            partNum = 1
        
            if ('lupaQuestionCounter' not in request.session):
                request.session['lupaQuestions'] = {}
                request.session['lupaQuestionCounter'] = 0

            request.session['lupaQuestionCounter']=request.session['lupaQuestionCounter']+1
            uniqid = str(request.session['lupaQuestionCounter'])

            lupaQuestionTable = request.session['lupaQuestions']
            
            if request.POST['_questionId']=='':
                questionIdString = "pleasesavebeforetesting"
            else:
                questionIdString = os.path.join(BASE_DIR, 'lua/problems/'+request.POST['_questionId']+'/')
            lupaQuestion = LupaQuestion(code,libs,seed,str(uniqid),numParts,questionIdString)
            if lupaQuestion.error is not None:
                errorInLupaQuestionConstructor = True
                tempError = lupaQuestion.error
            now = datetime.utcnow()
            qdict = { "uniqid": uniqid, "numParts":numParts, "lupaQuestion":lupaQuestion.serialize(), "dynamic_type":dynamic_type, "parts":dict(), 'creation':now.strftime("%m/%d/%Y %I:%M:%S %p") }
            if errorInLupaQuestionConstructor:
                qdict['error'] = tempError
            for i in range(1,numParts+1):
                qdict['parts'][str(i)] = {'submissionCount':0, 'maxpoints':Decimal(templateMaxPoints[i]) } 
                    # It's going to make i into a string when it gets stored in the sessions anyway (not sure why),

            lupaQuestionTable[uniqid] = qdict
            qdict['submissionsAllowed'] = convertStringOrTenIfBlank(request.POST['_submissionsAllowed'],int)
            qdict['resubmissionPenalty'] = convertStringOrTenIfBlank(request.POST['_resubmissionPenalty'],Decimal)
            qdict['point'] = convertStringOrTenIfBlank(request.POST.get('_points',Decimal(10)),Decimal)
            qdict['total_points'] = qdict['point']
            
            # We also take a moment or two to clear out old dynamic questions we were trying out.  Anything more than a week old gets
            # killed
            for k,v in list(request.session['lupaQuestions'].items()):
                if 'creation' in request.session['lupaQuestions'][k]:
                    creationtime = datetime.strptime(request.session['lupaQuestions'][k]['creation'],"%m/%d/%Y %I:%M:%S %p")
                    delta = now-creationtime
                    #print("\n\n\nLupa Session Stuff\nCreation:"+str(creationtime)+"\nnow:"+str(now)+"\ndelta.day:"+str(delta.days)+"\n\n")
                    if delta.days > 8:
                        del request.session['lupaQuestions'][k]
                else:
                    # So old that it predates the change to recording creation times.
                    del request.session['lupaQuestions'][k]
                            
        elif inTryOut: # We're trying out the question, but it already exists.
            uniqid = request.POST['_uniqid']
            lupaQuestionTable = request.session['lupaQuestions']
            qdict = lupaQuestionTable[uniqid]
            lupaQuestion = LupaQuestion.createFromDump(qdict["lupaQuestion"])
            if lupaQuestion.error is not None:
                qdict['error'] = lupaQuestion.error
                
        elif inChallenge: # We're in a challenge.  We don't need to create the question because that was done in questiontypes.py
            uniqid = request.POST['_uniqid']
            qdict = request.session[attemptId]["questions"][int(uniqid)-1]
            qdict['uniqid'] = uniqid # I think this is already set, but just in case, we're doing it again.
            lupaQuestion = LupaQuestion.createFromDump(qdict["lupaquestion"])
            if lupaQuestion.error is not None:
                qdict['error'] = lupaQuestion.error
                
        if partNum > 1:
            submissionCount = qdict['parts'][str(partNum-1)]['submissionCount'] + 1
            qdict['parts'][str(partNum-1)]['submissionCount'] = submissionCount
            if submissionCount > qdict['submissionsAllowed']:
                error_message = "<B>An error or some browser mischief has allowed the student to submit to a problem more times than allowed.  This additional submission will not be counted.</B>"
                return render(request,'Instructors/DynamicQuestionAJAXResult.html',{"error_message":error_message})
            
            # And now we need to evaluate the previous answers.
            answers = {}
            for value in request.POST:
                if not value.startswith("_"): 
                    answers[value] = request.POST[value]
            qdict['parts'][str(partNum-1)]["user_answers"] = answers
                        
            qdict['evaluations'] = lupaQuestion.answerQuestionPart(partNum-1, answers)
            if lupaQuestion.error is not None:
                qdict['error'] = lupaQuestion.error
                qdict['evaluations']=[]
                            
            earnedScore = 0
            numberIncorrect = 0
            for evaluation in qdict['evaluations']:
                if not evaluation['success']:
                    numberIncorrect += 1
                earnedScore += evaluation['value']

            def getMaxPointsForPart(p):
                if "maxpoints" in qdict['parts'][str(p)]:
                    return qdict['parts'][str(p)]['maxpoints']
                if qdict['dynamic_type'] == "raw_lua":
                    qdict['parts'][str(p)]['maxpoints'] = lupaQuestion.getPartMaxPoints(p)
                    if lupaQuestion.error is not None:
                        qdict['error'] = lupaQuestion.error 
                    return qdict['parts'][str(p)]['maxpoints']
            
            totalScore = getMaxPointsForPart(partNum-1)
                
            pointsRemaining = 0
            for i in range(partNum,qdict['numParts']+1):
                pointsRemaining += getMaxPointsForPart(i)
            
            maxTotalPointsAllParts = totalScore + pointsRemaining
            for i in range(1,partNum-1):
                maxTotalPointsAllParts += getMaxPointsForPart(i)
            
            retriesRemaining = qdict['submissionsAllowed'] - submissionCount
            nextPenalty = calcResubmissionPenalty(submissionCount,qdict)
            pointsPossible = nextPenalty * totalScore
            currentPenalty = calcResubmissionPenalty(submissionCount-1,qdict)

            problemScaleFactor = qdict['total_points']/maxTotalPointsAllParts
            qdict['evaluations'] = rescale_evaluations(qdict['evaluations'],problemScaleFactor*currentPenalty)
            qdict['parts'][str(partNum-1)]['evaluations'] = qdict['evaluations']
            qdict['sampleCorrect'] = lupaQuestion.getPartExampleAnswers(partNum-1)
            qdict['parts'][str(partNum-1)]['sampleCorrect'] = qdict['sampleCorrect']
            
            if numberIncorrect > 0:
                context_dict['failure'] = {
                    'numAnswerBlanksIncorrect':numberIncorrect,
                    'numAnswerBlanksTotal': len(qdict['evaluations']),
                    'pointsTotal': totalScore*problemScaleFactor*currentPenalty,
                    'pointsEarned': earnedScore*problemScaleFactor*currentPenalty,
                    'pointsPossible': pointsPossible*problemScaleFactor,
                    'pointsForFutureParts': pointsRemaining*problemScaleFactor,
                    'retriesRemaining': retriesRemaining,
                    'hadSomeRetries': submissionCount > 1
                }
                context_dict['retry'] = (retriesRemaining >= 1)
            elif earnedScore < totalScore:
                context_dict['partial_success'] = {
                    'pointsTotal': totalScore*problemScaleFactor*currentPenalty,
                    'pointsEarned': earnedScore*problemScaleFactor*currentPenalty,
                    'pointsPossible': pointsPossible*problemScaleFactor,
                    'pointsForFutureParts': pointsRemaining*problemScaleFactor,
                    'retriesRemaining': retriesRemaining
                }
                context_dict['retry'] = (retriesRemaining >= 1)
            else:
                context_dict['retry'] = False
        
        if not errorInLupaQuestionConstructor and partNum <= int(qdict["numParts"]):
            qdict['questionText'] = lupaQuestion.getQuestionPart(partNum)
            qdict['parts'][str(partNum)]['questionText'] = qdict['questionText']
        if 'error' not in context_dict and lupaQuestion.error is not None:
            #print("We are setting error to:" + str(lupaQuestion.error))
            qdict['error'] = lupaQuestion.error
        if not errorInLupaQuestionConstructor:
            if inTryOut:
                lupaQuestionTable[uniqid]['lupaQuestion']=lupaQuestion.serialize()
                request.session['lupaQuestions']=lupaQuestionTable
            elif inChallenge:
                request.session[attemptId]["questions"][int(uniqid)-1]["lupaquestion"]=lupaQuestion.serialize()
        
        if inChallenge and partNum == qdict["numParts"]+1:
            # We have just evaluated the last answer in a challenge
            user_points = 0
            for i in range(1,qdict["numParts"]+1):
                for evaluation in qdict["parts"][str(i)]["evaluations"]:
                    user_points += evaluation["value"]
            #print("\n\n Dynamic Problem stuff\nuser_points:"+str(user_points)+"\n\n")
            qdict["user_points"] = user_points
        
        context_dict['q'] = qdict
        context_dict['uniqid'] = uniqid
        context_dict['part'] = partNum
        return render(request,'Instructors/DynamicQuestionAJAXResult.html',context_dict)
