import random
import re
import json
from decimal import Decimal

from Instructors.models import Answers, StaticQuestions, MatchingAnswers, DynamicQuestions, CorrectAnswers, ChallengesQuestions

from Instructors.lupaQuestion import lupa_available, LupaQuestion, CodeSegment
from Students.models import StudentChallengeQuestions

class QuestionTypes():
    multipleChoice = 1
    multipleAnswers = 2
    matching = 3
    trueFalse = 4
    essay = 5
    dynamic = 6
    templatedynamic = 7
    parsons = 8
    questionTypes = {
        multipleChoice: {
            'index': multipleChoice,
            'name': 'multipleChoice',
            'displayName': 'Multiple Choice Questions',
        },
        multipleAnswers: {
            'index': multipleAnswers,
            'name': 'multipleAnswers',
            'displayName': 'Multiple Answer Questions',
        },
        matching: {
            'index': matching,
            'name': 'matching',
            'displayName': 'Matching Questions',
        },
        trueFalse: {
            'index': trueFalse,
            'name': 'trueFalse',
            'displayName': 'True/False Questions',
        },
        essay: {
            'index': essay,
            'name': 'essay',
            'displayName': 'Essay Questions',
        },
        dynamic: {
            'index': dynamic,
            'name': 'dynamic',
            'displayName': 'Dynamic Questions (Raw Lua)',
        },
        templatedynamic: {
            'index': templatedynamic,
            'name': 'templatedynamic',
            'displayName': 'Dynamic Questions (Template)',
        },
        parsons: {
            'index': parsons,
            'name': 'parsons',
            'displayName': 'Parsons Problems',
        },
    }


staticQuestionTypesSet = {
    QuestionTypes.matching, QuestionTypes.multipleAnswers,
    QuestionTypes.multipleChoice, QuestionTypes.trueFalse,
    QuestionTypes.parsons, QuestionTypes.essay
}
dynamicQuestionTypesSet = {
    QuestionTypes.dynamic, QuestionTypes.templatedynamic
}


def makeSerializableCopyOfDjangoObjectqdictionary(obj):
    qdict = obj.__dict__.copy()
    # We remove the Django Status object from the qdictionary to prevent serialization problems
    qdict.pop("_state", None)
    return qdict


def basicqdict(question, i, challengeId, studChallQuest):
    qdict = makeSerializableCopyOfDjangoObjectqdictionary(question)
    qdict['id'] = question.questionID
    qdict['index'] = i
    correct_answers = [
        makeSerializableCopyOfDjangoObjectqdictionary(ca)
        for ca in CorrectAnswers.objects.filter(questionID=question.questionID)
    ]
    print(correct_answers)
    canswer_range = range(1, len(correct_answers) + 1)
    qdict['correct_answers'] = list(zip(canswer_range, correct_answers))

    question_point = ChallengesQuestions.objects.get(
        challengeID=challengeId, questionID=question)
    qdict['point'] = question_point.points
    qdict['total_points'] = qdict['point']
    return qdict


def staticqdict(question, i, challengeId, studChallQuest):
    staticQuestion = StaticQuestions.objects.get(pk=question.questionID)
    qdict = basicqdict(staticQuestion, i, challengeId, studChallQuest)
    answers = [
        makeSerializableCopyOfDjangoObjectqdictionary(ans)
        for ans in Answers.objects.filter(questionID=question.questionID)
    ]
    if question.type != QuestionTypes.trueFalse:
        random.shuffle(answers)
    answer_range = range(1, len(answers) + 1)
    qdict['answers_with_count'] = list(zip(answer_range, answers))
    qdict['answers'] = answers
    return qdict


def matchingqdict(question, i, challengeId, studChallQuest):
    qdict = staticqdict(question, i, challengeId, studChallQuest)
    #getting the matching questions of the challenge from database
    matchlist = []
    for match in MatchingAnswers.objects.filter(
            questionID=question.questionID):
        matchdict = makeSerializableCopyOfDjangoObjectqdictionary(match)
        matchdict['answers_count'] = list(range(1, len(qdict['answers']) + 1))
        matchdict['answerText'] = match.answerID.answerText
        matchlist.append(matchdict)

    random.shuffle(matchlist)

    qdict['matches'] = []

    j = 1
    for matchqdict in matchlist:
        qdict['matches'].append(matchqdict)
        matchqdict['current_pos'] = j
        j = j + 1

    qdict['matches'] = matchlist
    return qdict


def parsonsqdict(question, i, challengeId, studChallQuest):
    qdict = staticqdict(question, i, challengeId, studChallQuest)
    modelSolution = Answers.objects.filter(questionID=question)
    solution_string = modelSolution[0].answerText


    qdict['languageName'] = re.search(
        r'Language:([^;]+)', solution_string).group(1).lower().lstrip()
    qdict['indentation'] = re.search(r';Indentation:([^;]+);',
                                     solution_string).group(1)

    languageAndLanguageName = re.search(r'Language:([^;]+)', solution_string)
    intentationEnabledVariableAndValue = re.search(r';Indentation:([^;]+);',
                                                   solution_string)
    solution_string = solution_string.replace(
        languageAndLanguageName.group(0), "")
    solution_string = solution_string.replace(
        intentationEnabledVariableAndValue.group(0), "")

    qdict['answerText'] = solution_string
    print("solution String before changes",repr(solution_string))
    #dynamically set dfficulty of parson distractor

    #get the count of the distractors

    distractorCount = len(
        re.findall(r'(?=#dist)',
                   repr(solution_string).strip('"\'')))
    qdict['distractorCount'] = distractorCount

    #set the count of distractors off the question's hardness
    if (question.difficulty == "Easy"):
        distractorCount = 0
        distractorCount = int(distractorCount / 2)

    qdict['distractorCount'] = distractorCount
    #if the question difficulty is hard,
    ##then we just use the full distractor count

    #repr function will give us the raw representation of the string
    print("Solution String", repr(solution_string))
    solution_string = re.sub("\t{3}", "☃            ", solution_string)
    solution_string = re.sub("\t{2}", "☃        ", solution_string)
    solution_string = re.sub("\t{1}", "☃    ", solution_string)

    #tokenizer characters ☃ and ¬
    solution_string = re.sub("\n", "\n¬☃", solution_string)
    solution_string = re.sub("^[ ]+?", "☃", solution_string)
    print("Solution String", solution_string)

    #we turn the student solution into a list
    solution_string = re.sub("(?<=\n)\t*", "   ", solution_string)
    solution_string = [x.strip() for x in solution_string.split('¬')]
    print("solutionString", solution_string)

    #give each string the new line
    tabedSolution_string = []

    #indentation flag allows checking to see if next line should be indented
    indentationFlag = 0
    pattern = re.compile("##")
    for line in solution_string:
        originalLine = line
        #we need the original line to match against when we find the next element
        line = re.sub("☃", "", line)
        if (indentationFlag == 1):
            #if indentation flag is 1 then we know that on this line we must indent
            indentationFlag = 0
            line = re.sub("^ *", '&nbsp;' + ' ' * 4, line)
        leadingSpacesCount = len(line) - len(line.lstrip(' '))
        if (pattern.search(line) != None):
            #get the net line, find out its spaces count
            nextelem = solution_string[solution_string.index(originalLine) + 1]
            nextelem = re.sub("☃", "", nextelem)
            leadingSpacesCountNextLine = len(nextelem) - len(
                nextelem.lstrip(' '))

            #we use the difference to calculate whether we must indent and where
            difference = leadingSpacesCount - leadingSpacesCountNextLine
            print("Difference", difference)
            if (difference == -4):
                #if indentation is after the line
                #ex:
                #data++;
                #   index++;
                indentationFlag = 1
            if (difference == 4):
                #if indentation is before the line
                #ex:
                #   data++;
                #index++;
                modifier = int(leadingSpacesCount / 2)
                if (modifier > 1 and leadingSpacesCount == 8):
                    #this modifier multiplies by the spaces count, if 8 then 4 in front, 4 after nbsp
                    #this is a quirk of parsons.js
                    line = re.sub("^ *", ' ' * modifier + '&nbsp;' + ' ' * 5,
                                  line)
                else:
                    line = re.sub("^ *", '&nbsp;' + ' ' * 4, line)
        print("line", repr(line))
        line = re.sub("\t(?=return.*; *##)", "&nbsp;    ", line)
        line = re.sub("(\s{4}|\t)(?=.* *##})", '&nbsp;' + ' ' * 4, line)
        line = line + "\n"
        tabedSolution_string.append(line)

    solution_string = ""
    solution_string = solution_string.join(tabedSolution_string)
    qdict['solution_string'] = solution_string
    qdict['tabbed_sol_string'] = tabedSolution_string
    print("tabbedSol String", tabedSolution_string)
    print("joinedSolString", repr(solution_string))

    solution_string = re.sub("##\\n *", "\\\\n", solution_string)
    solution_string = re.sub("\\\\n\t", "\\\\n", solution_string)
    solution_string = re.sub("(?<=\n)\s{4}", "\t", solution_string)
    qdict['model_solution'] = repr(solution_string).strip('\'')
    print("questqdict['model_solution']", qdict['model_solution'])

    return qdict


def dynamicqdict(question, i, challengeId, studChallQuest):
    dynamicQuestion = DynamicQuestions.objects.get(pk=question.questionID)
    qdict = basicqdict(dynamicQuestion, i, challengeId, studChallQuest)
    if not lupa_available:
        qdict[
            'questionText'] = "<B>Lupa not installed.  Please ask your server administrator to install it to enable dynamic problems.</B>"
    else:
        if studChallQuest is not None:
            seed = studChallQuest.seed
        else:
            seed = random.randint(-2147483647, 2147483646)
        qdict['seed'] = seed

        code = [CodeSegment.new(CodeSegment.raw_lua, dynamicQuestion.code, "")]
        numParts = dynamicQuestion.numParts
        from Instructors.views.dynamicQuestionView import makeLibs
        libs = makeLibs(dynamicQuestion)
        lupaQuest = LupaQuestion(code, libs, seed, str(i), numParts)

        #                            if (lupaQuest.error):
        #                                context_qdict['error']=lupaQuest.error
        #                                return render(request,'Instructors/DynamicQuestionAJAXResult.html',context_qdict)

        qdict['questionText'] = lupaQuest.getQuestionPart(1)
        qdict['lupaquestion'] = lupaQuest.serialize()
        qdict['requestType'] = '_eval'
        if numParts > 1:
            qdict['hasMultipleParts'] = True
        else:
            qdict['hasMultipleParts'] = False
    return qdict


def multipleChoiceMakeAnswerList(qdict, POST):
    correctAnswer = CorrectAnswers.objects.get(
        questionID=qdict['questionID']).answerID
    correctAnswerText = correctAnswer.answerText
    qdict['correct_answer_text'] = correctAnswerText

    answerInputName = str(qdict['index']) + '-ans'
    if answerInputName not in POST:
        studentAnswerList = []
    else:
        userSelection = int(POST[answerInputName])
        userAnswer = qdict['answers'][userSelection -
                                      1]  # Convert from 1-indexed to 0-indexed
        studentAnswerList = [str(userAnswer['answerID'])]
    return studentAnswerList


def multipleChoiceAnswersAndGrades(qdict, studentAnswers):
    correctAnswer = CorrectAnswers.objects.get(
        questionID=qdict['questionID']).answerID
    correctAnswerText = correctAnswer.answerText
    qdict['correct_answer_text'] = correctAnswerText
    if not studentAnswers:
        qdict['user_points'] = 0
        return qdict
    studentAnswerValue = studentAnswers[0]
    userSelection = 0
    userAnswer = {}
    # Loop through to find the student answer (AH)
    for index, answer in qdict['answers_with_count']:
        if answer['answerID'] == int(studentAnswerValue):
            userSelection = index
            userAnswer = answer
            break
    if not userAnswer:  # We didn't find the correct answer.
        qdict['user_answer'] = {
            'answerNumber':
            -1,
            'answerText':
            'Student selected answer which has since been deleted due to editing.  View will not match original grading.'
        }
    else:
        # answerNumber is used to match answer choices on the front-end (AH)
        qdict['user_answer'] = {
            'answerNumber': userSelection,
            'answerText': userAnswer['answerText']
        }

    # Check to see if the student answer matches the correct answer (AH)
    if int(studentAnswerValue) == correctAnswer.answerID:
        qdict['user_points'] = qdict['total_points']
    else:
        qdict['user_points'] = 0
    return qdict


def multipleChoiceCorrectAnswers(qdict):
    correctAnswer = CorrectAnswers.objects.get(
        questionID=qdict['questionID']).answerID
    correctAnswerText = correctAnswer.answerText
    qdict['correct_answer_text'] = correctAnswerText
    return qdict


def multipleAnswerMakeAnswerList(qdict, POST):
    answerInputName = str(qdict['index']) + '-ans'
    userAnswerIndexes = POST.getlist(answerInputName)

    if not userAnswerIndexes:
        return []
    else:
        userAnswerIndexes = [int(x) for x in userAnswerIndexes]
        userAnswerIds = [
            qdict['answers'][x - 1]['answerID'] for x in userAnswerIndexes
        ]
        return userAnswerIds


def multipleAnswerAddAnswersAndGrades(qdict, studentAnswers):
    correctAnswers = [
        x.answerID
        for x in CorrectAnswers.objects.filter(questionID=qdict['questionID'])
    ]
    correctAnswerIds = [x.answerID for x in correctAnswers]
    qdict['correct_answer_texts'] = [x.answerText for x in correctAnswers]

    # Finding the student answers (AH)
    userAnswerIndexes = []
    userAnswers = []
    for stuAns in studentAnswers:
        for index, answer in qdict['answers_with_count']:
            if answer['answerID'] == int(stuAns):
                userAnswerIndexes.append(index)
                userAnswers.append((index, answer))
                break

    userAnswerIndexes = [int(x) for x in userAnswerIndexes]
    userAnswerIds = [x['answerID'] for i, x in userAnswers]

    numAnswersIncorrect = len(
        [x for x in userAnswerIds if x not in correctAnswerIds])
    numAnswersMissing = len(
        [x for x in correctAnswerIds if x not in userAnswerIds])

    valuePerAnswer = qdict['total_points'] / len(qdict['answers'])

    qdict['user_points'] = round(
        qdict['total_points'] -
        valuePerAnswer * (numAnswersIncorrect + numAnswersMissing), 2)
    qdict['user_answers'] = [{
        'answerNumber': i,
        'answerText': x['answerText']
    } for i, x in userAnswers]
    return qdict


def multipleAnswerCorrectAnswers(qdict):
    correctAnswers = [
        x.answerID
        for x in CorrectAnswers.objects.filter(questionID=qdict['questionID'])
    ]
    correctAnswerIds = [x.answerID for x in correctAnswers]
    qdict['correct_answer_texts'] = [x.answerText for x in correctAnswers]
    return qdict


def matchingMakeAnswerList(qdict, POST):
    studentAnswerList = []

    i = 1
    for match in qdict['matches']:
        if match is not None:
            answerInputName = str(qdict['index']) + '-' + str(i)
            userAnswerIndex = int(POST[answerInputName])
            studentAnswerList.append(
                str(match['matchingAnswerID']) + ":" +
                str(qdict['answers'][userAnswerIndex - 1]['answerID']))
        i = i + 1

    return studentAnswerList


def matchingAddAnswersAndGrades(qdict, studentAnswers):
    userAnswers = []
    userScore = []
    matches = qdict['matches']
    valuePerAnswer = qdict['total_points'] / len(qdict['answers'])
    userScore = 0
    for match in matches:
        if match is not None:
            # Find correct answer
            correctAnswerIndex = 0
            for index, answer in qdict['answers_with_count']:
                if answer['answerID'] == match['answerID_id']:
                    correctAnswerIndex = index
                    break

            # Find student answer that matches with the current match object (AH)
            for stuAns in studentAnswers:
                userAnswerIndex = 0
                matchAnswer = stuAns
                parts = matchAnswer.split(':')

                for index, answer in qdict['answers_with_count']:
                    if answer['answerID'] == int(
                            parts[1]) and match['matchingAnswerID'] == int(
                                parts[0]):
                        userAnswerIndex = index
                        break
                if userAnswerIndex != 0:
                    break
            userAnswers.append({
                'answerNumber':
                userAnswerIndex,
                'answerText':
                MatchingAnswers.objects.get(pk=parts[0]).answerID.answerText
            })
            if correctAnswerIndex == userAnswerIndex:
                userScore = userScore + valuePerAnswer

    qdict['user_points'] = round(userScore, 2)
    qdict['user_answers'] = userAnswers
    return qdict


def trueFalseMakeAnswerList(qdict, POST):
    answerInputName = str(qdict['index']) + '-ans'
    if answerInputName not in POST:
        return []
    else:
        return [str(POST[answerInputName] == 't')]


def trueFalseAddAnswersAndGrades(qdict, studentAnswers):
    correctAnswerValue = CorrectAnswers.objects.get(
        questionID=qdict['questionID']).answerID.answerText == "true"
    qdict['correctAnswerText'] = str(correctAnswerValue)

    if not studentAnswers:
        qdict['user_points'] = 0
        return qdict
    studentAnswerValue = str(studentAnswers[0])
    qdict['user_answer'] = {
        'answerText': studentAnswerValue,
        'answerValue': studentAnswerValue == 'True'
    }
    if studentAnswerValue == str(correctAnswerValue):
        qdict['user_points'] = qdict['total_points']
    else:
        qdict['user_points'] = 0
    return qdict


def trueFalseCorrectAnswers(qdict):
    correctAnswerValue = CorrectAnswers.objects.get(
        questionID=qdict['questionID']).answerID.answerText == "true"
    qdict['correctAnswerText'] = str(correctAnswerValue)
    return qdict


def dynamicMakeAnswerList(qdict, POST):
    if not qdict['hasMultipleParts']:
        answers = {}
        for value in POST:
            indexstring = str(qdict['index'])
            if value.startswith(indexstring + "-"):
                answers[value[len(indexstring) + 1:]] = POST[value]
        studentAnswerList = [
            key + ":" + answers[key] for key in answers.keys()
        ]
    else:
        studentAnswerList = []
    return studentAnswerList


def dynamicAnswersAndGrades(qdict, studentAnswers):
    if lupa_available:
        lupaQuestion = LupaQuestion.createFromDump(qdict['lupaquestion'])
        if qdict['numParts'] == 1:
            answers = {}
            for ans in studentAnswers:
                answerParts = ans.split(":")
                answers[answerParts[0]] = answerParts[1]
            print(studentAnswers)
            qdict['user_answers'] = answers
            qdict['evaluations'] = lupaQuestion.answerQuestionPart(1, answers)
            if qdict['evaluations']:
                qdict['user_points'] = sum(
                    [eval['value'] for eval in qdict['evaluations']])
            else:
                qdict['user_points'] = 0
        else:
            qdict['user_points'] = 0
    return qdict


def parsonsMakeAnswerList(qdict, POST):
    #get all the data from the webpage
    #data is accessed through the index
    studentAnswerDict = {}
    lineIndent = POST[str(qdict['index']) + 'lineIndent']
    studentAnswerDict['lineIndent'] = lineIndent
    studentSolutions = POST[str(qdict['index']) + 'studentSol']
    wrongPositionLineNumberbers = POST[str(qdict['index']) + 'lineNo']
    studentAnswerDict[
        'wrongPositionLineNumberbers'] = wrongPositionLineNumberbers
    errorDescriptions = POST[str(qdict['index']) + 'errorDescription']
    studentAnswerDict['errorDescriptions'] = errorDescriptions
    correctLineCount = POST[str(qdict['index']) + 'correctLineCount']
    studentAnswerDict['correctLineCount'] = correctLineCount
    feedBackButtonClickCount = POST[str(qdict['index']) +
                                    'feedBackButtonClickCount']
    studentAnswerDict['feedBackButtonClickCount'] = feedBackButtonClickCount

    correctLineCount = int(correctLineCount)
    feedBackButtonClickCount = int(feedBackButtonClickCount)

    studentAnswer = ""
    #if the student ddnt fill in any solution, zero points
    if studentSolutions != "":
        #let us begin with a good clean copy of the information
        solution_string = qdict['answerText']
        print("solution_string", repr(solution_string))

        #perform regex magic on solution string
        # logical not ¬ is the item that splits the code
        # ᚛ is used to preserve new lines, they dissapear in the code
        # ⋊ is used to maintain the indentation of the line, so that we can later remove it
        # but still keep proper indentation in each line
        #if it contains a block treat it as a unit
        solution_string = re.sub("(?<!##|?!.*return result;##)\n", "᚛¬⋊", solution_string)
        solution_string = re.sub(";(?!.+)", "᚛", solution_string)
        
        print("solution_stringrepr", repr(solution_string))
        print("solution_string", solution_string)
        solution_string_array = []
        solution_string_split = [x.strip() for x in solution_string.split('¬')]
        for line in solution_string_split:
            print("line:",repr(line))
            line = re.sub("^⋊\s*(?!.*;\s*##)", "", line)
            line = re.sub("^⋊(\t\t|\s{8})(?=.*;\s*##)", "    ", line)
            line = re.sub("^⋊(\t|\s{4})(?=.*;\s*##)(?!return)", "", line)
            line = re.sub("⋊\t(?=return.*\s*##\n})", "    ", line)
            print("line unchanged:", repr(line))
            line = re.sub("^((?!\s*return)(?=.* *##\n}))", "    ", line)
            line = re.sub("᚛", "\n", line)
            line = re.sub("⋊", "", line)
            line = re.sub("##", "", line)
            #for some mysterious reason ace editor hates commas,
            #we had to use a special comma to allow it to be visisble
            line = re.sub("(?!\"),(?=.*\";)", "‚", line)
            solution_string_array.append(line)

        print("solution_string_array", repr(solution_string_array))

        
        lineIndent = [x.strip() for x in lineIndent.split(',')]
        print("LineIndent", lineIndent)
        studentSolutions = [x.strip() for x in studentSolutions.split(',')]

        print("studentSol", studentSolutions)
        studentAnswerDict['parsonStudentSol'] = studentSolutions
        regexp = re.compile(r'##')
        missingLines = []
        missingLineCount = 1
        duplicateIndentation = False
        tabbed_sol = ""
        i = 0
        doesTheEntireThingHaveZeroIndetation = True
        for lineIndentObject in lineIndent:
            if int(lineIndentObject) != 0:
                doesTheEntireThingHaveZeroIndetation = False
                break
        
        pattern = re.compile("##")
        for studentSolution in studentSolutions:
            ##print("studentSolution", studentSolution)
            ##print("i", i)
            ##print("int(lineIndent[i]) + solution_string_array[int(studentSolution)])",int(lineIndent[i]), solution_string_array[int(studentSolution)])
            tabbed_sol = ("\t" * int(lineIndent[i]) + solution_string_array[int(studentSolution)])
            studentAnswer +=  tabbed_sol
            i+=1
        #print("studentAnswer", studentAnswer)
    studentAnswerDict['studentSolution'] = studentAnswer
    return [json.dumps(studentAnswerDict)]


def parsonsAddAnswersAndGrades(qdict, studentAnswers):
    qdict = parsonsCorrectAnswers(qdict)

    answer = Answers.objects.filter(questionID=qdict['questionID'])
    answer = answer[0].answerText
    print("Model Solution: ", answer)

    #get the language information and indentation status
    #remove the first line that keeps the data
    searchString = re.search(r'Language:([^;]+);Indentation:([^;]+);', answer)
    answer = re.sub("##", "", answer)
    indentation = searchString.group(2)

    studentAnswerDict = json.loads(studentAnswers[0])
    studentAnswer = studentAnswerDict['studentSolution']
    studentSolution = studentAnswer
    lineIndentRegex = re.search(r'IndentationArray:([^;]+);', studentAnswer)
    if (lineIndentRegex != None):
        lineIndent = lineIndentRegex.group(1)
        studentAnswer = studentAnswer.replace(lineIndentRegex.group(0), "")

    else:
        lineIndent = '[' + '0,' * 15 + '0]'

    lineIndent = re.findall('\d+', lineIndent)
    qdict["lineIndent"] = lineIndent

    #we turn the student solution into a list
    studentAnswer = [x.strip() for x in studentAnswer.split(',')]
    #make a list of lines, split on , so we know how much to indent where
    lineIndent = [int(line) for line in lineIndent]

    #perform the spacing for each line
    IndentedStudentSolution = []
    for index, line in enumerate(studentAnswer, 0):
        line = '    ' * lineIndent[index] + line + '\n'
        IndentedStudentSolution.append(line)

    studentAnswer = ""
    studentAnswer = studentAnswer.join(IndentedStudentSolution)

    qdict['student_solution'] = studentAnswer
    print("student solution", repr(qdict['student_solution']))

    wrongPositionLineNumberbers = studentAnswerDict['wrongPositionLineNumberbers']
    errorDescriptions = studentAnswerDict['errorDescriptions']
    correctLineCount = int(studentAnswerDict['correctLineCount'])
    feedBackButtonClickCount = int(studentAnswerDict['feedBackButtonClickCount'])
    print("correctlinecount", correctLineCount,wrongPositionLineNumberbers,errorDescriptions,feedBackButtonClickCount)
    studentGrade = 0.0
    penalties = 0.0
    if studentSolution == "" or studentSolution == '\n':
        qdict['user_points'] = 0
#        print("activated")
    else:
        ##if no errors happened give them full credit
        if (errorDescriptions == ""):
            studentGrade = qdict['total_points']

        ##otherwise grade on our criteria
        else:
            indentationErrorCount = len(re.findall(r'(?=i.e. indentation)', repr(errorDescriptions)))
            ##grading section
            studentGrade = qdict['total_points']
            maxPoints = qdict['total_points']
            penalties = Decimal(0.0)

            studentSolutionLineCount = len(studentAnswerDict['parsonStudentSol'])

            ##too few
            if (studentSolutionLineCount < correctLineCount):
                penalties += Decimal((correctLineCount - studentSolutionLineCount) * (1 / correctLineCount))
                print("Penalties too few!: ", penalties)
            ##too many
            if (studentSolutionLineCount > correctLineCount):
                penalties += Decimal((studentSolutionLineCount - correctLineCount) * (1 / correctLineCount))
                print("Penalties too many!: ", penalties)

            if wrongPositionLineNumberbers:
                wrongPositionLineNumberbers = [x.strip() for x in wrongPositionLineNumberbers.split(',')]
                penalties += Decimal( len(wrongPositionLineNumberbers) / correctLineCount)
                print("WrongLineNumber length:", len(wrongPositionLineNumberbers))
                print("WrongLine Number penalties: ", penalties)

            ##if there was an indentation problem
            if indentation == "true":
                if indentationErrorCount > 0:
                    ##we multiply by 1/2 because each wrong is half of 1/n
                    penalties += Decimal((indentationErrorCount / correctLineCount) * (1/2))

            print("Student grade:", studentGrade)
            print("Total Points:", qdict['total_points'])
            if feedBackButtonClickCount > 0:
                maxPoints /= feedBackButtonClickCount * 2
            else:
                maxPoints = qdict['total_points']
        
            #max points is the maximum points student can earn, and we subtract the penalties
            print("studentGrade", studentGrade, maxPoints, penalties)
            studentGrade = float(maxPoints) - (float(maxPoints) * float(penalties))
            if studentGrade < 0:
                studentGrade = 0
    
        qdict['user_points'] = round(Decimal(studentGrade), 2)
    return qdict


def parsonsCorrectAnswers(qdict):
    answer = Answers.objects.filter(questionID=qdict['questionID'])
    answer = answer[0].answerText
    print("Model Solution: ", answer)

    #get the language information and indentation status
    #remove the first line that keeps the data
    searchString = re.search(r'Language:([^;]+);Indentation:([^;]+);', answer)
    answer = re.sub("##", "", answer)
    answer = answer.replace(searchString.group(0), "")

    answer = re.sub("^ *\\t", "  ", answer)

    #tokenizer characters ☃ and ¬
    answer = re.sub("\n", "\n¬☃", answer)
    answer = re.sub("^[ ]+?", "☃", answer)

    #we turn the student solution into a list
    answer = [x.strip() for x in answer.split('¬')]

    #get how many spaces there are in the first line
    answer[0] = re.sub("☃", " ", answer[0])
    leadingSpacesCount = len(answer[0]) - len(answer[0].lstrip(' '))

    #give each string the new line
    tabedanswer = []
    for index, line in enumerate(answer):
        line = re.sub("☃", "", line)
        line = re.sub(".*#distractor", "", line)
        line = re.sub("^[ ]{" + str(leadingSpacesCount) + "}", "", line)
        if index < len(answer) - 1:
            line = line + "\n"
        tabedanswer.append(line)

    answer = ""
    answer = answer.join(tabedanswer)

    qdict['model_solution'] = answer
    return qdict


questionTypeFunctions = {
    QuestionTypes.multipleChoice: {
        "makeqdict": staticqdict,
        "makeAnswerList": multipleChoiceMakeAnswerList,
        "studentAnswersAndGrades": multipleChoiceAnswersAndGrades,
        "correctAnswers": multipleChoiceCorrectAnswers,
    },
    QuestionTypes.multipleAnswers: {
        "makeqdict": staticqdict,
        "makeAnswerList": multipleAnswerMakeAnswerList,
        "studentAnswersAndGrades": multipleAnswerAddAnswersAndGrades,
        "correctAnswers": multipleAnswerCorrectAnswers,
    },
    QuestionTypes.matching: {
        "makeqdict": matchingqdict,
        "makeAnswerList": matchingMakeAnswerList,
        "studentAnswersAndGrades": matchingAddAnswersAndGrades,
        "correctAnswers": lambda qdict: qdict,  # Already done in makeqdict
    },
    QuestionTypes.trueFalse: {
        "makeqdict": staticqdict,
        "makeAnswerList": trueFalseMakeAnswerList,
        "studentAnswersAndGrades": trueFalseAddAnswersAndGrades,
        "correctAnswers": trueFalseCorrectAnswers,
    },
    QuestionTypes.essay: {
        "makeqdict": basicqdict,
        "makeAnswerList": lambda qdict, POST: [],
        "studentAnswersAndGrades": lambda qdict, studentAnswers: qdict,
        "correctAnswers": lambda qdict: qdict,
    },
    QuestionTypes.dynamic: {
        "makeqdict": dynamicqdict,
        "makeAnswerList": dynamicMakeAnswerList,
        "studentAnswersAndGrades": dynamicAnswersAndGrades,
        "correctAnswers": lambda qdict: qdict,
    },
    QuestionTypes.templatedynamic: {
        "makeqdict": dynamicqdict,
        "makeAnswerList": dynamicMakeAnswerList,
        "studentAnswersAndGrades": dynamicAnswersAndGrades,
        "correctAnswers": lambda qdict: qdict,
    },
    QuestionTypes.parsons: {
        "makeqdict": parsonsqdict,
        "makeAnswerList": parsonsMakeAnswerList,
        "studentAnswersAndGrades": parsonsAddAnswersAndGrades,
        "correctAnswers": parsonsCorrectAnswers,
    },
}