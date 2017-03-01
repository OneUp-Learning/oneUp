'''
Created on Apr 1, 2014

@author: irwink
'''

from django.template import RequestContext
from django.shortcuts import render, redirect
from django.http import HttpResponse

from Instructors.models import TemplateDynamicQuestions, Challenges,ChallengesQuestions, Courses
from Instructors.lupaQuestion import LupaQuestion, lupa_available 

from Instructors.views import utils


from Badges.enums import QuestionTypes

from django.views.decorators.csrf import csrf_exempt
import sys
import re


def templateDynamicQuestionForm(request):
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
                         'instructorNotes','setupCode','templateQuestion','numParts'];

    if request.POST:
        
        # If there's an existing question, we wish to edit it.  If new question,
        # create a new Question object.
        if 'questionId' in request.POST:
            question = TemplateDynamicQuestions.objects.get(pk=int(request.POST['questionId']))
        else:
            question = TemplateDynamicQuestions()

        # Copy all strings from POST to database object.
        for attr in string_attributes:
            setattr(question,attr,request.POST[attr])
        
        #used to fill in info for question text 
        question.questonText = ''  
        
        # get the author                            # 03/10/2015
        if request.user.is_authenticated():
            question.author = request.user.username
        else:
            question.author = ""
                 
        question.code = templateToCode(question.setupCode,question.templateText)
    
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
                context_dict['difficulty'] = 'Easy'
    
                
        # If questionId is specified then we load for editing.
        if 'questionId' in request.GET:
            question = TemplateDynamicQuestions.objects.get(pk=int(request.GET['questionId']))
            
            # Copy all of the attribute values into the context_dict to
            # display them on the page.
            context_dict['questionId']=request.GET['questionId']
            for attr in string_attributes:
                context_dict[attr]=getattr(question,attr)
        else:
            context_dict["setupCode"] = "r1 = math.random(10) + 1 \nr2 = math.random(10) + 1"
            context_dict["templateQuestion"] = "What is [{print(r1)}] + [{print(r2)}]? [{make_answer('ans1','int',5,exact_equality(r1+r2),10)}]"
            context_dict["numParts"] = 1
            
        
    
    #question = LupaQuestion(code,[],5,"edit",1)
    #context_dict["test"] = question.getQuestionPart(1);
    
    if 'questionId' in request.POST:         
            return redirect('challengesView')
            
    return render(request,'Instructors/TemplateDynamicQuestionForm.html', context_dict)

def makePartHTMLwithForm(question,part):
    formHead = '<form name="'+question.uniqid+'" id="'+question.uniqid+'" action="doDynamicQuestion" method="POST" onSubmit="submit_form(\''+question.uniqid+'\');return false;" >'
    formBody = '<input type="hidden" name="_part" value="'+str(part+1)+'">'
    formBody += '<input type="hidden" name="_uniqid" value="'+question.uniqid+'">'
    formBody += question.getQuestionPart(part)
    formBody += '<input type="submit" name="submit" value="Submit" class="button"> </form><div id="phase2"></div>'
    return (formHead,formBody)
    
# First we set up a regular expression to separate the templateQuestion into parts.
# We do this here rather than in the function because we would rather have it only run once
# since the regular expression is always the same.
templateRegex = re.compile(r"\[\{(.*?)\}\]",re.DOTALL)
def templateToCode(setupCode,templateQuestion):
    pieces = re.split(templateRegex,templateQuestion)
    i = 1
    code = '''
        exact_equality = function(a)
            return function(b,pts)
                if tonumber(a)==tonumber(b) then
                    return {success=true,value=pts}
                else
                    return {success=false,value=0}
                end
            end
        end
            
        _answer_checkers = {}
        _pts = {}
        make_answer = function(name,type,size,checker,pts)
            _answer_checkers[name] = checker
            _pts[name] = pts
            print(make_input(name,type,size))
        end
        part_1_max_points = function()
            local sum = 0
            for k,v in pairs(_pts) do
                sum = sum + v
            end
            return sum
        end
        evaluate_answer_1 = function(answers)
            results = {}
            for inputName in python.iter(answers) do
                results[inputName] = _answer_checkers[inputName](answers[inputName],_pts[inputName])
            end
            return results
        end
    '''
    code += setupCode + "\n" # Newline added to help readability
    code += '''
part_1_text = function ()
    output = ""
    '''
    #TODO: escape quotation marks from pieces
    code += "print('"+pieces[0]+"')\n"
    l = len(pieces)  # l will always be odd because of how split works when parenthesis are used in the regular expression
    while i<l:
        code += pieces[i] + "\n"
        i += 1
        code += "print('"+pieces[i]+"')\n"
        i += 1
    code += ' _debug_print("answer checkers") _debug_print(_answer_checkers["ans1"]) '
    code += 'end'
    print("CODE")
    print(code)
    return code