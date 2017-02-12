'''
Created on Apr 1, 2014

@author: irwink
'''

from django.template import RequestContext
from django.shortcuts import render
from django.http import HttpResponse

from Instructors.models import DynamicQuestions
from Instructors.lupaQuestion import LupaQuestion

from Badges.enums import QuestionTypes

from django.views.decorators.csrf import csrf_exempt
import sys


def dynamicQuestionForm(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
    context = RequestContext(request)
    context_dict = { }

    # In this class, these are the names of the attributes which are strings.
    # We put them in an array so that we can copy them from one item to
    # another programmatically instead of listing them out.
    string_attributes = ['preview','questionText','difficulty','correctAnswerFeedback', # 04/09
                         'instructorNotes','author','code','numParts'];

    if request.POST:

        # If there's an existing question, we wish to edit it.  If new question,
        # create a new Question object.
        if request.POST['questionId']:
            question = DynamicQuestions.objects.get(pk=int(request.POST['questionId']))
        else:
            question = DynamicQuestions()

        # Copy all strings from POST to database object.
        for attr in string_attributes:
            setattr(question,attr,request.POST[attr])
                   
        # Fix the question type
        question.type = QuestionTypes.dynamic
        question.save();  #Writes to database.
    
    elif request.method == 'GET':
                
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

    #question = LupaQuestion(code,[],5,"edit",1)
    #context_dict["test"] = question.getQuestionPart(1);

    return render(request,'Instructors/DynamicQuestionForm.html', context_dict)

def makePartHTMLwithForm(question,part):
    formHead = '<form name="'+question.uniqid+'" id="'+question.uniqid+'" action="doDynamicQuestion" method="POST" onSubmit="submit_form(\''+question.uniqid+'\');return false;" >'
    formBody = '<input type="hidden" name="_part" value="'+str(part+1)+'">'
    formBody += '<input type="hidden" name="_uniqid" value="'+question.uniqid+'">'
    formBody += question.getQuestionPart(part)
    formBody += '<input type="submit" name="submit" value="Submit" class="button"> </form><div id="phase2"></div>'
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

    if request.method == 'POST':
        uniqid = request.POST['_uniqid']
        if ('_testeval' in request.POST):
            part = int(request.POST['_part'])
            requesttype = '_testeval'
        elif ('_eval' in request.POST):
            part = int(request.POST['_part'])
            requesttype = '_eval'
        elif ('_test' in request.POST):
            code = request.POST['_code']
            seed = request.POST['_seed']
            numParts = request.POST['_numParts']
            libs = []
            part = 1
            requesttype = '_testeval'
        elif ('_init' in request.POST):
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
            if ('uniqid' not in lupaQuestionTable):
                lupaQuestion = LupaQuestion(code,libs,seed,uniqid,numParts)
                lupaQuestionTable[uniqid]=lupaQuestion.serialize()
                request.session['lupaQuestions']=lupaQuestionTable
            else:
                lupaQuestion = LupaQuestion.createFromDump(lupaQuestionTable[uniqid])
            theresult = ''
        else:
            lupaQuestion = LupaQuestion.createFromDump(request.session['lupaQuestions'][uniqid])
            # And now we need to evaluate the previous answers.
            answers = {}
            for value in request.POST:
                if (value.startswith(uniqid+"_")): 
                    answers[value[len(uniqid)+1:]] = request.POST[value]
            evaluations = lupaQuestion.answerQuestionPart(part-1, answers)
            theresult = ''
            for answer in evaluations:
                theresult += "You got "+str(evaluations[answer]['value'])+" points on answer "+answer
            print(theresult)
                   
        context_dict['theresult'] = theresult           
        formhead,formbody = makePartHTMLwithForm(lupaQuestion,part)
        context_dict['formhead'] = formhead
        context_dict['formbody'] = formbody
        context_dict['uniqid'] = uniqid
        context_dict['part'] = part
        context_dict['type'] = requesttype
        
        if (part==1):
            return render(request,'Instructors/DynamicQuestionAJAX.html',context_dict)
        else:
            return render(request,'Instructors/DynamicQuestionAJAXResult.html',context_dict)
        
