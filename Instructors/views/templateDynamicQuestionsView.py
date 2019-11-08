'''
Created on Apr 1, 2014

@author: irwink
'''

from django.shortcuts import render, redirect

from Instructors.models import TemplateDynamicQuestions, Challenges, ChallengesQuestions, TemplateTextParts, LuaLibrary, QuestionLibrary, QuestionProgrammingFiles
from Instructors.lupaQuestion import CodeSegment
from django.http import HttpResponse
from Instructors.views import utils
from Instructors.constants import unassigned_problems_challenge_name, default_time_str, unlimited_constant

from Badges.enums import ObjectTypes
from Instructors.questionTypes import QuestionTypes

import re
from django.contrib.auth.decorators import login_required, user_passes_test
from decimal import Decimal
from oneUp.decorators import instructorsCheck
from oneUp.ckeditorUtil import config_ck_editor
import os.path
import zipfile
from oneUp.settings import BASE_DIR


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def templateDynamicQuestionForm(request):
    context_dict, currentCourse = utils.initialContextDict(request)

    # In this view, these are the names of the attributes which are just passed through with no processing.
    # We put them in an array so that we can copy them from one item to
    # another programmatically instead of listing them out.
    passthrough_attributes = ['preview', 'difficulty',
                              'instructorNotes', 'setupCode', 'numParts', 'author', 'submissionsAllowed', 'resubmissionPenalty']

    context_dict['skills'] = utils.getCourseSkills(currentCourse)
    context_dict['tags'] = []
    if request.POST:
        # If there's an existing question, we wish to edit it.  If new question,
        # create a new Question object.
        if 'questionId' in request.POST:
            question = TemplateDynamicQuestions.objects.get(
                pk=int(request.POST['questionId']))
            isModifying = True
        else:
            question = TemplateDynamicQuestions()
            isModifying = False

        # Copy all strings from POST to database object.
        for attr in passthrough_attributes:
            setattr(question, attr, request.POST[attr])

        # used to fill in info for question text
        question.questonText = ''

        # if user did not specify author of the question, the author will be the user
        if question.author == '':
            question.author = request.user.username

        question.save()  # Writes to database.

        if request.FILES:
            print('we got files')
            files = request.FILES.getlist('testFile')
            saveFiles(currentCourse, question, files,
                      request.user, isModifying)

        # loops through and adds the multiple parts(the actual text) into to the template array
        templateArray = []
        partPointsArray = []
        numTemplateParts = int(request.POST['numParts'])
        # the 1 is the start of the range and we need to go all the way to the numparts (inclusive)
        for i in range(1, numTemplateParts+1):
            templateArray.append(request.POST['templateTextVisible'+str(i)])
            partPointsArray.append(int(request.POST['partpoints'+str(i)]))

        def combineCodeSegments(codeSegments):
            output = ""
            for codeSegment in codeSegments:
                output += codeSegment['code']
                output += "\n"
            return output

        # Add the path of the question files directroy to the programinterface.program_checker
        '''LUA_PROBLEMS_ROOT = os.path.join(
            BASE_DIR, 'lua/problems/')  # This is for lua problems
        LUA_PROBLEMS_ROOT = "/Users/mahamatoumar/Downloads/oneUp_env/env/oneUp/lua/problems/" + \
            str(question.questionID)

        setupCode = re.sub("programinterface.program_checker\s*\(",
                           "programinterface.program_checker("+LUA_PROBLEMS_ROOT+",", question.setupCode)
        print("Replaced setupCode")
        print(setupCode)'''

        # Takes the array and converts the parts into lua code
        question.code = combineCodeSegments(
            templateToCodeSegments(question.setupCode, templateArray))

        # Fix the question type
        question.type = QuestionTypes.templatedynamic
        question.save()  # Writes to database.

        # Query that gets all objects that are in foreign key relation to the question and deletes them all
        TemplateTextParts.objects.filter(dynamicQuestion=question).delete()

        # Used for the number of parts in the array
        count = int(1)

        # make a new object that is a part and add all the fields it needs
        for text, partpoints in zip(templateArray, partPointsArray):
            textPart = TemplateTextParts()
            textPart.partNumber = count
            textPart.dynamicQuestion = question
            textPart.templateText = text
            textPart.pointsInPart = partpoints
            textPart.save()
            count += 1

        # Processing and saving tags in DB
        utils.saveTags(request.POST['tags'], question, ObjectTypes.question)

        if 'challengeID' in request.POST:
            # save in ChallengesQuestions if not already saved

            position = ChallengesQuestions.objects.filter(
                challengeID=request.POST['challengeID']).count() + 1

            positions = []
            if  'questionId' in request.POST:      
                # Delete challenge question (even duplicates)                     
                challenge_questions = ChallengesQuestions.objects.filter(challengeID=request.POST['challengeID']).filter(questionID=request.POST['questionId'])
                for chall_question in challenge_questions:
                    positions.append(chall_question.questionPosition)
                
                challenge_questions.delete()

            challengeID = request.POST['challengeID']
            challenge = Challenges.objects.get(pk=int(challengeID))
            if positions:
                # Recreate challenge question (and duplicates)
                for pos in positions:
                    ChallengesQuestions.addQuestionToChallenge(question, challenge, Decimal(request.POST['points']), pos)
            else:
                ChallengesQuestions.addQuestionToChallenge(question, challenge, Decimal(request.POST['points']), position)

            # Processing and saving skills for the question in DB
            utils.addSkillsToQuestion(currentCourse, question, request.POST.getlist(
                'skills[]'), request.POST.getlist('skillPoints[]'))

            makeDependentLibraries(
                question, request.POST.getlist('dependentLuaLibraries[]'))

            redirectVar = redirect(
                '/oneUp/instructors/challengeQuestionsList', context_dict)
            redirectVar['Location'] += '?challengeID=' + \
                request.POST['challengeID']
            return redirectVar

        # Question is unassigned so create unassigned challenge object
        challenge = Challenges()
        challenge.challengeName = unassigned_problems_challenge_name
        challenge.courseID = currentCourse
        challenge.startTimestamp = utils.utcDate(
            default_time_str, "%m/%d/%Y %I:%M %p")
        challenge.endTimestamp = utils.utcDate(
            default_time_str, "%m/%d/%Y %I:%M %p")
        challenge.numberAttempts = unlimited_constant
        challenge.timeLimit = unlimited_constant
        challenge.save()
        ChallengesQuestions.addQuestionToChallenge(question, challenge, 0, 0)

        redirectVar = redirect(
            '/oneUp/instructors/challengeQuestionsList?problems', context_dict)
        return redirectVar

    elif request.method == 'GET':
        if 'view' in request.GET:
            context_dict['view'] = request.GET['view']
        context_dict['luaLibraries'] = getAllLuaLibraryNames()
        context_dict["initalTemplateTextPart"] = "What is [|r1|] + [|r2|]? [{make_answer('ans1','number',5,exact_equality(r1+r2),10,r1+r2)}]"
        context_dict['checkInitalTemplateTextPart'] = True

        if Challenges.objects.filter(challengeID=request.GET['challengeID'], challengeName=unassigned_problems_challenge_name):
            context_dict["unassign"] = 1

        if 'challengeID' in request.GET:
            context_dict['challengeID'] = request.GET['challengeID']
            chall = Challenges.objects.get(
                pk=int(request.GET['challengeID']))
            context_dict['challengeName'] = chall.challengeName
            context_dict['challenge'] = True

        # If questionId is specified then we load for editing.
        if 'questionId' in request.GET:
            question = TemplateDynamicQuestions.objects.get(
                pk=int(request.GET['questionId']))

            # Copy all of the attribute values into the context_dict to
            # display them on the page.
            context_dict['questionId'] = request.GET['questionId']
            for attr in passthrough_attributes:
                context_dict[attr] = getattr(question, attr)

            # TODO: get all matching templateTextPart objects and then add their code to the
            # context dictionary as templateTextParts
            # get form the database the matching question for the parts
            templateTextParts = TemplateTextParts.objects.filter(
                dynamicQuestion=question)
            context_dict['templateTextParts'] = templateTextParts
            context_dict['checkInitalTemplateTextPart'] = False

            context_dict['selectedLuaLibraries'] = getLibrariesForQuestion(
                question)

            testFiles = QuestionProgrammingFiles.objects.filter(
                questionID=question)
            testFileIDs = []
            testFileNames = []
            if(testFiles):
                for f in testFiles:
                    testFileIDs.append(f.programmingFileID)
                    testFileNames.append(f.programmingFileName)

            context_dict['programmingFiles'] = zip(testFileIDs, testFileNames)
            # Extract the tags from DB
            context_dict['tags'] = utils.extractTags(question, "question")

            if 'challengeID' in request.GET:
                # get the challenge points for this problem to display
                challenge_questions = ChallengesQuestions.objects.filter(
                    challengeID=request.GET['challengeID']).filter(questionID=request.GET['questionId'])
                context_dict['points'] = challenge_questions[0].points

                # set default skill points - 1
                context_dict['q_skill_points'] = int('1')

                # Extract the skill
                context_dict['selectedSkills'] = utils.getSkillsForQuestion(
                    currentCourse, question)

        else:
            context_dict['difficulty'] = 'Easy'
            context_dict["setupCode"] = "r1 = math.random(10) + 1 \nr2 = math.random(10) + 1"
            context_dict["numParts"] = 1
            context_dict['tags'] = []

    # question = LupaQuestion(code,[],5,"edit",1)
    # context_dict["test"] = question.getQuestionPart(1);

    if 'questionId' in request.POST:
        return redirect('challengesView')

    context_dict['ckeditor'] = config_ck_editor()

    return render(request, 'Instructors/TemplateDynamicQuestionForm.html', context_dict)


def HTMLquotesToRegularQuotes(str):
    return str.replace(r"&#39;", "'", 10000).replace(r'&quot;', '"', 10000)


# First we set up a regular expression to separate the templateText into parts.
# We do this here rather than in the function because we would rather have it only run once
# since the regular expression is always the same.
templateCodeSplitRegex = re.compile(r"\[\{(.*?)\}\]", re.DOTALL)
templateVarSplitRegex = re.compile(r"\[\|(.*?)\|\]", re.DOTALL)


def templateToCodeSegments(setupCode, templateArray):
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
        _sampleans = {}
        make_answer = function(name,type,size,checker,pts,sampleans)
            _answer_checkers[_part][name] = checker
            _pts[_part][name] = pts
            _sampleans[_part][name] = sampleans
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
                    results[inputName] = _answer_checkers[part][inputName](
                        answers[inputName],_pts[part][inputName])
                end
                return results
            end
        end
        _part_example_answers = function(part)
            return function()
                return _sampleans[part]
            end
        end
    '''
    code_segments.append(CodeSegment.new(CodeSegment.system_lua, sys_code, ""))
    code_segments.append(CodeSegment.new(CodeSegment.template_setup_code,
                                         setupCode + "\n", ""))  # Newline added to help readability

    count = int(1)

    for templateText in templateArray:
        code = ""
        code += 'part_'+str(count) + \
            '_max_points = _part_max_points('+str(count)+')\n'
        code += 'evaluate_answer_' + \
            str(count)+' = _evaluate_answer('+str(count)+')\n'
        code += 'part_' + \
            str(count)+'_example_answers = _part_example_answers('+str(count)+')\n'
        code += '''
part_'''+str(count)+'''_text = function ()
    _part = '''+str(count)+'''
    _answer_checkers[_part] = {}
    _pts[_part] = {}
    _sampleans[_part] = {}
    output = ""
    '''

        code_segments.append(CodeSegment.new(CodeSegment.system_lua, code, ""))
        count += 1
        # First we split out the variable eval parts and convert them to code print statements
        pieces = re.split(templateVarSplitRegex, templateText)
        templateTextNoValues = pieces[0]
        i = 1
        # l will always be odd because of how split works when parenthesis are used in the regular expression
        l = len(pieces)
        value_comment = '\n--value\n'
        while i < l:
            templateTextNoValues += "[{"+value_comment+"print("+pieces[i]+")}]"
            i += 1
            templateTextNoValues += pieces[i]
            i += 1

        pieces = re.split(templateCodeSplitRegex, templateTextNoValues)
        # TODO: escape quotation marks from pieces
        piece_code = "print([======["+pieces[0]+"]======])\n"
        code_segments.append(CodeSegment.new(CodeSegment.template_richtext,
                                             piece_code, pieces[0]))
        i = 1
        # l will always be odd because of how split works when parenthesis are used in the regular expression
        l = len(pieces)
        while i < l:
            piece_code = HTMLquotesToRegularQuotes(pieces[i]) + "\n"
            if pieces[i].startswith(value_comment):
                piece_type = CodeSegment.template_expression
            else:
                piece_type = CodeSegment.template_code
            code_segments.append(CodeSegment.new(
                piece_type, piece_code, pieces[i]))
            i += 1
            piece_code = "print([======["+pieces[i]+"]======])\n"
            code_segments.append(CodeSegment.new(CodeSegment.template_richtext,
                                                 piece_code, pieces[i]))
            i += 1

        code_segments.append(CodeSegment.new(
            CodeSegment.system_lua, "end\n", ""))
    return code_segments


def getAllLuaLibraryNames():
    return [ll.libraryName for ll in LuaLibrary.objects.all()]


def getLibrariesForQuestion(question):
    return [ql.library.libraryName for ql in QuestionLibrary.objects.filter(question=question)]


def makeDependentLibraries(question, libraryNameList):
    existingDeps = list(map(lambda x: x.library.libraryName,
                            QuestionLibrary.objects.filter(question=question)))
    namesWithoutExisting = [
        val for val in libraryNameList if val not in existingDeps]
    existingWithoutNames = [
        val for val in existingDeps if val not in libraryNameList]
    for name in namesWithoutExisting:
        ql = QuestionLibrary()
        ql.question = question
        ql.library = LuaLibrary.objects.get(libraryName=name)
        ql.save()
    for name in existingWithoutNames:
        QuestionLibrary.objects.filter(
            question=question, library__libraryName=name).delete()


def saveFiles(courseID, question, files, user, isModifying):

    LUA_PROBLEMS_ROOT = os.path.join(
        BASE_DIR, 'lua/problems/')  # This is for lua problems

    FILE_UPLOAD_DIR = LUA_PROBLEMS_ROOT + \
        str(question.questionID)

    if not isModifying:
        # define the access rights
        access_rights = 0o755
        try:
            os.mkdir(FILE_UPLOAD_DIR, access_rights)
        except:
            print("Creation of the directory %s failed" % FILE_UPLOAD_DIR)
            return
        else:
            print("Successfully created the directory %s" % FILE_UPLOAD_DIR)

    for f in files:
        fileName = f.name
        print("filename", fileName)
        if ".zip" in fileName:
            print("for zip file", fileName)
            with zipfile.ZipFile(f, 'r') as zipf:
                zipf.extractall(FILE_UPLOAD_DIR)

        completeDirName = os.path.join(FILE_UPLOAD_DIR, fileName)

        # if file with the same name already exists, remove it
        if os.path.exists(completeDirName):
            os.remove(completeDirName)
            relatedFile = QuestionProgrammingFiles.objects.filter(
                questionID=question, programmingFileName=fileName)
            for rF in relatedFile:
                rF.delete()

        try:
            if not ".zip" in fileName:
                theFile = open(completeDirName, "w")
                theFile.write(str(f.read(), 'utf-8'))
                theFile.close()
            testFile = QuestionProgrammingFiles()
            testFile.questionID = question
            testFile.programmingFileName = fileName
            testFile.programmingFileUploader = user
            testFile.programmingFileFolderName = str(question.questionID)
            testFile.save()

        except:
            continue

    '''for f in files:
        fileName = f.name
        if ".head" in fileName or ".tail" in fileName:
            print("for head or tail", fileName)
            testFile = TestProblemFiles()
            testFile.questionID = question
            testFile.testProblemFile = f
            testFile.testProblemFileName = fileName
            testFile.testProblemFileUploader = user
            testFile.save()

        else:
            print("model", fileName)
            testFile = TestProblemModelFiles()
            testFile.questionID = question
            testFile.testProblemModelFile = f
            testFile.testProblemModelFileName = fileName
            testFile.testProblemModelFileUploader = user
            testFile.save()
    print("done saving files")'''


@login_required
@user_passes_test(instructorsCheck, login_url='/oneUp/students/StudentHome', redirect_field_name='')
def removeFileFromQuestion(request):
    import shutil
    if request.user.is_authenticated:
        if request.POST:

            if 'fileID' in request.POST and 'fileName' in request.POST:
                fileID = request.POST['fileID']
                testFile = QuestionProgrammingFiles.objects.get(
                    programmingFileID=int(fileID))
                fileName = testFile.programmingFileName
                folderName = testFile.programmingFileFolderName
                testFile.delete()
                LUA_PROBLEMS_ROOT = os.path.join(
                    BASE_DIR, 'lua/problems/')  # This is for lua problems

                if ".zip" in fileName:
                    subDir = fileName.split(".zip")[0]
                    FILE_UPLOAD_DIR = LUA_PROBLEMS_ROOT + \
                        folderName+"/"+subDir
                    if os.path.exists(FILE_UPLOAD_DIR):
                        shutil.rmtree(FILE_UPLOAD_DIR)

                else:
                    FILE_UPLOAD_DIR = LUA_PROBLEMS_ROOT + \
                        folderName+"/"+fileName
                    if os.path.exists(FILE_UPLOAD_DIR):
                        os.remove(FILE_UPLOAD_DIR)

                return HttpResponse(200)
            else:
                return HttpResponse(403, 'something went wrong')
        return HttpResponse(403, 'something went wrong')
    else:
        return HttpResponse(403)
