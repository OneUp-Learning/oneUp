'''
Created on Apr 1, 2014

@author: irwink
'''

from django.template import RequestContext
from django.shortcuts import render, redirect
from django.http import HttpResponse

from Instructors.models import DynamicQuestions, Challenges,ChallengesQuestions, Courses
from Instructors.lupaQuestion import LupaQuestion, lupa_available 

from Instructors.views import utils
from Instructors.views.templateDynamicQuestionsView import templateToCode

from Badges.enums import QuestionTypes

from django.views.decorators.csrf import csrf_exempt
import sys


def dynamicQuestionForm(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
    context = RequestContext(request)
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
    string_attributes = ['preview','difficulty','correctAnswerFeedback', # 04/09
                         'instructorNotes','code','numParts'];

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
                skillString = request.POST.get('newSkills', "default")
                utils.saveQuestionSkills(skillString, question, challenge)
    
            # Processing and saving tags in DB
            tagString = request.POST.get('tags', "default")
            utils.saveQuestionTags(tagString, question)
            
            redirectVar = redirect('/oneUp/instructors/challengeQuestionsList', context_dict)
            redirectVar['Location']+= '?challengeID='+request.POST['challengeID']
            return redirectVar
    
    elif request.method == 'GET':
                
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
        else:
            code = '''\
part_1_text = function ()
    return 'What is 1+1?' .. make_input('answer1','int',10)
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



    #question = LupaQuestion(code,[],5,"edit",1)
    #context_dict["test"] = question.getQuestionPart(1);
    
    if 'questionId' in request.POST:         
            return redirect('challengesView')
            
    return render(request,'Instructors/DynamicQuestionForm.html', context_dict)

def makePartHTMLwithForm(question,part):
    formHead = ('<form name="'+question.uniqid+'-'+str(part)+'" id="'+question.uniqid+'" action="doDynamicQuestion" method="POST" onSubmit="submit_form(\''+
                question.uniqid+'\','+str(part)+');disableDiv(\''+question.uniqid+'-'+str(part)+'\');return false;" >')
    formBody = '<input type="hidden" name="_part" value="'+str(part+1)+'">'
    formBody += '<input type="hidden" name="_uniqid" value="'+question.uniqid+'">'
    formBody += question.getQuestionPart(part)
    formBody += '<input type="submit" name="submit" value="Submit" class="button"> </form>'
    return (formHead,formBody)

def makePartHTMLwithoutForm(question,part):
    qhtml = question.getQuestionPart(part)
    return qhtml

def dynamicQuestionGetPartNonAJAX():
    return ""

def makeLibs(dynamicQuestion):
# Dynamic Library support is incomplete.  We'll add this soon.  For now we just return an empty list.
#    libs = LibraryToQuestion.objects.filter(question=dynamicQuestion)
    output = []
#    for lib in libs:
#        output.append(lib.name)
    return output

def dynamicQuestionPartAJAX(request):
    context_dict = { }
    if not lupa_available:
        context_dict['theresult'] = "<B>Lupa not installed.  Please ask your server adminstrator to install it to enable dynamic problems.</B>"
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
                code = request.POST['_code']
            else:
                code = templateToCode(request.POST['_setupCode'],request.POST['_templateText'])
            seed = request.POST['_seed']
            numParts = request.POST['_numParts']
            libs = []
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
            
            lupaQuestion = LupaQuestion(code,libs,seed,uniqid,numParts)
            theresult = ''
        else:
            lupaQuestionTable = request.session['lupaQuestions']
            lupaQuestion = LupaQuestion.createFromDump(lupaQuestionTable[uniqid])
            # And now we need to evaluate the previous answers.
            answers = {}
            for value in request.POST:
                if (value.startswith(uniqid+"_")): 
                    answers[value[len(uniqid)+1:]] = request.POST[value]
            evaluations = lupaQuestion.answerQuestionPart(part-1, answers)
            
            #starts of making the table for the web page 
            theresult = '<table class="bg">'
            for answer in evaluations:
                theresult+= '<tr><td> '
                if(evaluations[answer]['success']):
                    theresult += " <span style='color: green;'>&#10004;</span>You got "+str(evaluations[answer]['value'])+" points on answer "+answer #prints with an check 
                else:
                    theresult += " <span style='color: red;'>&#10006;</span>You got "+str(evaluations[answer]['value'])+" points on answer "+answer #prints with an X  
                if 'details' in evaluations[answer]:
                    details = evaluations[answer]["details"]
                    for testName in details.keys():
                        print(details[testName]['success'])
                        print(details[testName]['value'])
                        print(details[testName]['max_points'])
                        
                theresult+='</tr></td>'
            
            theresult+= '</table>'
            print(theresult)
                   
        context_dict['theresult'] = theresult
        
        formhead,formbody = makePartHTMLwithForm(lupaQuestion,part)
        lupaQuestionTable[uniqid]=lupaQuestion.serialize()
        request.session['lupaQuestions']=lupaQuestionTable
        
        context_dict['formhead'] = formhead
        context_dict['formbody'] = formbody
        context_dict['uniqid'] = uniqid
        context_dict['part'] = part
        context_dict['partplusone'] = part+1
        context_dict['type'] = requesttype
        
        if (part==1):
            return render(request,'Instructors/DynamicQuestionAJAX.html',context_dict)
        else:
            return render(request,'Instructors/DynamicQuestionAJAXResult.html',context_dict)
        
