'''
Created on Apr 1, 2014

@author: irwink
'''

from django.template import RequestContext
from django.shortcuts import render, redirect

from Instructors.models import TemplateDynamicQuestions, Challenges,ChallengesQuestions, Courses, TemplateTextParts
from Instructors.models import LuaLibrary, QuestionLibrary
from Instructors.lupaQuestion import LupaQuestion, lupa_available, CodeSegment

from Instructors.views import utils

from Badges.enums import QuestionTypes

import re
from django.contrib.auth.decorators import login_required

@login_required
def templateDynamicQuestionForm(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
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
                         'instructorNotes','setupCode','numParts','author'];

    context_dict['skills'] = utils.getCourseSkills(currentCourse)
    
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
        
        # if user did not specify author of the question, the author will be the user
        if question.author == '':
            question.author = request.user.username
            
        question.save();  #Writes to database.
           
        #loops through and adds the multiple parts(the actual text) into to the template array   
        templateArray = [] 
        for i in range(1,int(request.POST['numParts'])+1): # the 1 is the start of the rang and we need to go all the way to the numparts+1
            templateArray.append(request.POST['templateTextVisible'+str(i)])
            
        def combineCodeSegments(codeSegments):
            output = ""
            for codeSegment in codeSegments:
                output += codeSegment['code']
                output += "\n"
            return output
        
        #Takes the array and converts the parts into lua code            
        question.code = combineCodeSegments(templateToCodeSegments(question.setupCode,templateArray))
    
        # Fix the question type
        question.type = QuestionTypes.templatedynamic
        question.save();  #Writes to database.
        
        #Query that gets all objects that are in foreign key relation to the question and deletes them all 
        TemplateTextParts.objects.filter(dynamicQuestion=question).delete()
        
            
        #Used for the number of parts in the array    
        count = int(1)
        
        #make a new object that is a part and add all the fields it needs
        for text in templateArray:
            textPart = TemplateTextParts() 
            textPart.partNumber = count
            textPart.dynamicQuestion = question 
            textPart.templateText = text 
            textPart.save()
            count+= 1
        
        
        if 'challengeID' in request.POST:
            # save in ChallengesQuestions if not already saved            
            
            position = ChallengesQuestions.objects.filter(challengeID=request.POST['challengeID']).count() + 1
            
            if  'questionId' in request.POST:                         
                challenge_question = ChallengesQuestions.objects.filter(challengeID=request.POST['challengeID']).filter(questionID=request.POST['questionId'])
                for chall_question in challenge_question:
                    position = chall_question.questionPosition
                
                challenge_question.delete()

            challengeID = request.POST['challengeID']
            challenge = Challenges.objects.get(pk=int(challengeID))
            ChallengesQuestions.addQuestionToChallenge(question, challenge, int(request.POST['points']) , position)
                            
            # Processing and saving skills for the question in DB
            utils.addSkillsToQuestion(currentCourse,question,request.POST.getlist('skills[]'),request.POST.getlist('skillPoints[]'))
    
            # Processing and saving tags in DB
            tagString = request.POST.get('tags', "default")
            utils.saveQuestionTags(tagString, question)
            
            makeDependentLibraries(question,request.POST.getlist('dependentLuaLibraries[]'))
            
            redirectVar = redirect('/oneUp/instructors/challengeQuestionsList', context_dict)
            redirectVar['Location']+= '?challengeID='+request.POST['challengeID']
            return redirectVar
    
    elif request.method == 'GET':
        
        context_dict['luaLibraries'] = getAllLuaLibraryNames();
        
        context_dict["initalTemplateTextPart"] = "What is [|r1|] + [|r2|]? [{make_answer('ans1','number',5,exact_equality(r1+r2),10)}]"
        context_dict['checkInitalTemplateTextPart'] = True
        
        if Challenges.objects.filter(challengeID = request.GET['challengeID'],challengeName="Unassigned Problems"):
                context_dict["unassign"]= 1
                
        if 'challengeID' in request.GET:
                context_dict['challengeID'] = request.GET['challengeID']
                chall = Challenges.objects.get(pk=int(request.GET['challengeID']))
                context_dict['challengeName'] = chall.challengeName
                context_dict['challenge'] = True    
    
                
        # If questionId is specified then we load for editing.
        if 'questionId' in request.GET:
            question = TemplateDynamicQuestions.objects.get(pk=int(request.GET['questionId']))
            
            # Copy all of the attribute values into the context_dict to
            # display them on the page.
            context_dict['questionId']=request.GET['questionId']
            for attr in string_attributes:
                context_dict[attr]=getattr(question,attr)
            
            # TODO: get all matching templateTextPart objects and then add their code to the 
            # context dictionary as templateTextParts
            templateTextParts = TemplateTextParts.objects.filter(dynamicQuestion=question) #get form the databse the matching question for the parts
            context_dict['templateTextParts']=templateTextParts
            context_dict['checkInitalTemplateTextPart'] = False
            
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
                context_dict['selectedSkills'] = utils.getSkillsForQuestion(currentCourse,question)                    
           
            
        else:
            context_dict['difficulty'] = 'Easy'
            context_dict["setupCode"] = "r1 = math.random(10) + 1 \nr2 = math.random(10) + 1"
            context_dict["numParts"] = 1
            
        
    
    #question = LupaQuestion(code,[],5,"edit",1)
    #context_dict["test"] = question.getQuestionPart(1);
    
    if 'questionId' in request.POST:         
            return redirect('challengesView')
            
    return render(request,'Instructors/TemplateDynamicQuestionForm.html', context_dict)

def HTMLquotesToRegularQuotes(str):
    return str.replace(r"&#39;","'",10000).replace(r'&quot;','"',10000)

# First we set up a regular expression to separate the templateText into parts.
# We do this here rather than in the function because we would rather have it only run once
# since the regular expression is always the same.
templateCodeSplitRegex = re.compile(r"\[\{(.*?)\}\]",re.DOTALL)
templateVarSplitRegex = re.compile(r"\[\|(.*?)\|\]",re.DOTALL)
def templateToCodeSegments(setupCode,templateArray):
    code_segments = list()
    sys_code = '''
        exact_equality = function(a)
            return function(b,pts)
                if tonumber(a)==tonumber(b) then
                    return {success=true,value=pts}
                else
                    return {success=false,value=0}
                end
            end
        end

        approximate_equality = function(a,fudgefraction)
            return function(b,pts)
                a = tonumber(a)
                b = tonumber(b)
                if a == 0 then
                    if b <= fudgefraction and b >= -fudgefraction then
                        return {success=true,value=pts}
                    else
                        return {success=false,value=0}
                    end
                else
                    if math.abs((a-b)/a)<=fudgefraction then
                        return {success=true,value=pts}
                    else
                        return {success=false,value=0}
                    end
                end
            end
        end
            
        _answer_checkers = {}
        _pts = {}
        make_answer = function(name,type,size,checker,pts)
            _answer_checkers[_part][name] = checker
            _pts[_part][name] = pts
            print(make_input(name,type,size))            
        end
        _part_max_points = function(part)
            return function()
                local sum = 0
                for k,v in pairs(_pts[part]) do
                    sum = sum + v
                end
                return sum
            end
        end
        _evaluate_answer = function(part)
            return function(answers)
                results = {}
                for inputName in python.iter(answers) do
                    results[inputName] = _answer_checkers[part][inputName](answers[inputName],_pts[part][inputName])
                end
                return results
            end
        end
    '''
    code_segments.append(CodeSegment.new(CodeSegment.system_lua,sys_code,""))
    code_segments.append(CodeSegment.new(CodeSegment.template_setup_code,
                                         setupCode + "\n", "")) # Newline added to help readability
   
    count = int(1)

    for templateText in templateArray:
        code = ""
        code += 'part_'+str(count)+'_max_points = _part_max_points('+str(count)+')\n'
        code += 'evaluate_answer_'+str(count)+' = _evaluate_answer('+str(count)+')\n'
        code += '''
part_'''+str(count)+'''_text = function ()
    _part = '''+str(count)+'''
    _answer_checkers[_part] = {}
    _pts[_part] = {}
    
    output = ""
    '''

        code_segments.append(CodeSegment.new(CodeSegment.system_lua,code,""))
        count+=1
         # First we split out the variable eval parts and convert them to code print statements
        pieces = re.split(templateVarSplitRegex,templateText)
        templateTextNoValues = pieces[0]
        i = 1
        l = len(pieces)  # l will always be odd because of how split works when parenthesis are used in the regular expression
        value_comment = '\n--value\n'
        while i<l:
            templateTextNoValues += "[{"+value_comment+"print("+pieces[i]+")}]";
            i += 1
            templateTextNoValues += pieces[i]
            i += 1
            
        pieces = re.split(templateCodeSplitRegex,templateTextNoValues)
        #TODO: escape quotation marks from pieces
        piece_code = "print([======["+pieces[0]+"]======])\n"
        code_segments.append(CodeSegment.new(CodeSegment.template_richtext,
                                             piece_code,pieces[0]))
        i = 1
        l = len(pieces)  # l will always be odd because of how split works when parenthesis are used in the regular expression
        while i<l:
            piece_code = HTMLquotesToRegularQuotes(pieces[i]) + "\n"
            if pieces[i].startswith(value_comment):
                piece_type = CodeSegment.template_expression
            else:
                piece_type = CodeSegment.template_code
            code_segments.append(CodeSegment.new(piece_type,piece_code,pieces[i]))
            i += 1
            piece_code = "print([======["+pieces[i]+"]======])\n"
            code_segments.append(CodeSegment.new(CodeSegment.template_richtext,
                                                  piece_code,pieces[i]))
            i += 1
    
        code_segments.append(CodeSegment.new(CodeSegment.system_lua, "end\n", ""))

    return code_segments

def getAllLuaLibraryNames():
    return [ll.libraryName for ll in LuaLibrary.objects.all()]

def getLibrariesForQuestion(question):
    return [ql.library.libraryName for ql in QuestionLibrary.objects.filter(question=question)]

def makeDependentLibraries(question,libraryNameList):
    existingDeps = list(map(lambda x:x.library.libraryName,QuestionLibrary.objects.filter(question=question)))
    namesWithoutExisting = [val for val in libraryNameList if val not in existingDeps]
    existingWithoutNames = [val for val in existingDeps if val not in libraryNameList]
    for name in namesWithoutExisting:
        ql = QuestionLibrary()
        ql.question = question
        ql.library = LuaLibrary.objects.get(libraryName = name)
        ql.save()
    for name in existingWithoutNames:
        QuestionLibrary.objects.filter(question=question,library__libraryName=name).delete()
    