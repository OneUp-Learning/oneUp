'''
Created on Apr 1, 2014

@author: irwink
'''

from django.shortcuts import render, redirect
from django.http import HttpResponse

from Instructors.models import DynamicQuestions, Challenges,ChallengesQuestions, Courses, QuestionLibrary
from Instructors.lupaQuestion import LupaQuestion, lupa_available, CodeSegment

from Instructors.views import utils
from Instructors.views.templateDynamicQuestionsView import templateToCodeSegments, getAllLuaLibraryNames, getLibrariesForQuestion, makeDependentLibraries

from Badges.enums import QuestionTypes

from django.views.decorators.csrf import csrf_exempt
import sys
from xml.dom.expatbuilder import theDOMImplementation
from django.contrib.auth.decorators import login_required

@login_required


def dynamicQuestionForm(request):
    context_dict = { }
    
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict['username']=request.user.username

    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected'

    # In this class, these are the names of the attributes which are strings.
    # We put them in an array so that we can copy them from one item to
    # another programmatically instead of listing them out.
    string_attributes = ['preview','difficulty',
                         'instructorNotes','code','numParts'];

    context_dict['skills'] = utils.getCourseSkills(currentCourse)

    if request.POST:

        # If there's an existing question, we wish to edit it.  If new question,
        # create a new Question object.
        if 'questionId' in request.POST:
            question = DynamicQuestions.objects.get(pk=int(request.POST['questionId']))
        else:
            question = DynamicQuestions()

        # Copy all strings from POST to database object.
        for attr in string_attributes:
            setattr(question,attr,request.POST[attr])
        question.questionText = ""  
        
        # get the author                            # 03/10/2015
        if request.user.is_authenticated():
            question.author = request.user.username
        else:
            question.author = ""
                 
        # Fix the question type
        question.type = QuestionTypes.dynamic
        question.save();  #Writes to database.
        
        if 'challengeID' in request.POST:
            # save in ChallengesQuestions if not already saved        # 02/28/2015    
            
            if  'questionId' in request.POST:                         
                challenge_question = ChallengesQuestions.objects.filter(challengeID=request.POST['challengeID']).filter(questionID=request.POST['questionId'])
                challenge_question.delete()

            challengeID = request.POST['challengeID']
            challenge = Challenges.objects.get(pk=int(challengeID))
            ChallengesQuestions.addQuestionToChallenge(question, challenge, int(request.POST['points']))

            # save question-skill pair to db                    # 03/01/2015
            # first need to check whether a new skill is selected 
            
            if request.session['currentCourseID']:          # we presume the course is selected!!!!!!!!!!!!!!!!!!!!!!!!!
                courseID = Courses.objects.get(pk=int(request.session['currentCourseID']))
                
                # Processing and saving skills for the question in DB
                utils.addSkillsToQuestion(challenge,question,request.POST.getlist('skills[]'),request.POST.getlist('skillPoints[]'))
    
            # Processing and saving tags in DB
            tagString = request.POST.get('tags', "default")
            utils.saveQuestionTags(tagString, question)
            
            makeDependentLibraries(question,request.POST.getlist('dependentLuaLibraries[]'))
            
            redirectVar = redirect('/oneUp/instructors/challengeQuestionsList', context_dict)
            redirectVar['Location']+= '?challengeID='+request.POST['challengeID']
            return redirectVar
    
    elif request.method == 'GET':
        
        context_dict['luaLibraries'] = getAllLuaLibraryNames();
        
        if Challenges.objects.filter(challengeID = request.GET['challengeID'],challengeName="Unassigned Problems"):
            context_dict["unassign"]= 1
                
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
            for attr in string_attributes:
                context_dict[attr]=getattr(question,attr)
                
            context_dict['selectedLuaLibraries'] = getLibrariesForQuestion(question)

            # Extract the tags from DB
            context_dict['tags'] = utils.extractTags(question, "question")

            if 'challengeID' in request.GET:
                # get the challenge points for this problem to display
                challenge_questions = ChallengesQuestions.objects.filter(challengeID=request.GET['challengeID']).filter(questionID=request.GET['questionId'])
                context_dict['points'] = challenge_questions[0].points
                    
                # set default skill points - 1
                context_dict['q_skill_points'] = int('1')

                # Extract the skill                                        
                context_dict['selectedSkills'] = utils.getSkillsForQuestion(request.GET['challengeID'],question) 

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
    
    if 'questionId' in request.POST:         
            return redirect('challengesView')
            
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
            formBody += questionpart
    formBody += '<input type="submit" name="submit" value="Submit" class="button"> </form>'
    return (formHead,formBody)

def makePartHTMLwithoutForm(question,part):
    qhtml = question.getQuestionPart(part)
    return qhtml

def dynamicQuestionGetPartNonAJAX():
    return ""

def makeLibs(dynamicQuestion):
    libs = QuestionLibrary.objects.filter(question=dynamicQuestion)
    return [lib.library.libraryName for lib in libs]

def dynamicQuestionPartAJAX(request):
    context_dict = { }
    if not lupa_available:
        context_dict['theresult'] = "<B>Lupa not installed.  Please ask your server administrator to install it to enable dynamic problems.</B>"
        return render(request,'Instructors/DynamicQuestionAJAXResult.html',context_dict)

    if request.method == 'POST':
        print(request.POST)
        uniqid = request.POST['_uniqid']
        if ('_testeval' in request.POST):
            part = int(request.POST['_part'])
            requesttype = '_testeval'
        elif ('_eval' in request.POST):
            part = int(request.POST['_part'])
            requesttype = '_eval'
        elif ('_test' in request.POST):
            if '_code' in request.POST:
                code = [CodeSegment.new(CodeSegment.raw_lua,request.POST['_code'],"")]
            else:
                numParts = int(request.POST['_numParts'])
                templateParts = []
                for i in range(1,numParts+1):
                    templateParts.append(request.POST['_templateText'+str(i)])
                code = templateToCodeSegments(request.POST['_setupCode'],templateParts)
            seed = request.POST['_seed']
            numParts = request.POST['_numParts']
            libs = request.POST.getlist('_dependentLuaLibraries[]')
            part = 1
            requesttype = '_testeval'
        elif ('_init' in request.POST):
            print("We are in INIT")
            questionID = request.POST['questionID']
            seed = request.POST['seed']
            dynamicQuestion = DynamicQuestions.objects.get(pk=questionID)
            code = dynamicQuestion.code
            numParts = dynamicQuestion.num_parts
            libs = makeLibs(dynamicQuestion)
            part = 1
            requesttype = '_eval'
        
        if (part == 1):
            if ('lupaQuestions' not in request.session):
                request.session['lupaQuestions'] = {}
            
            lupaQuestionTable = request.session['lupaQuestions']
            
            errorInLupaQuestionConstructor = False
            lupaQuestion = LupaQuestion(code,libs,seed,uniqid,numParts)
            if lupaQuestion.error is not None:
                errorInLupaQuestionConstructor = True
        else:
            lupaQuestionTable = request.session['lupaQuestions']
            lupaQuestion = LupaQuestion.createFromDump(lupaQuestionTable[uniqid])
            
            # And now we need to evaluate the previous answers.
            answers = {}
            for value in request.POST:
                if (value.startswith(uniqid+"-")): 
                    answers[value[len(uniqid)+1:]] = request.POST[value]
            evaluations = lupaQuestion.answerQuestionPart(part-1, answers)
            if lupaQuestion.error is not None:
                context_dict['error'] = lupaQuestion.error
            
            #starts of making the table for the web page 
            context_dict['evaluations'] = evaluations
            
            errorInLupaQuestionConstructor = False
        
        if not errorInLupaQuestionConstructor:
            formhead,formbody = makePartHTMLwithForm(lupaQuestion,part)
        else:
            formhead = ""
            formbody = ""
        if 'error' not in context_dict and lupaQuestion.error is not None:
            #print("We are setting error to:" + str(lupaQuestion.error))
            context_dict['error'] = lupaQuestion.error
        if not errorInLupaQuestionConstructor:
            lupaQuestionTable[uniqid]=lupaQuestion.serialize()
            request.session['lupaQuestions']=lupaQuestionTable
        
        context_dict['formhead'] = formhead
        context_dict['formbody'] = formbody
        context_dict['uniqid'] = uniqid
        context_dict['part'] = part
        context_dict['partplusone'] = part+1
        context_dict['type'] = requesttype
        
        return render(request,'Instructors/DynamicQuestionAJAXResult.html',context_dict)
        
