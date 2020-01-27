import random
import re
import json
import os
from decimal import Decimal
from random import shuffle
from Instructors.models import Answers, StaticQuestions, MatchingAnswers, DynamicQuestions, CorrectAnswers, ChallengesQuestions, TemplateDynamicQuestions, TemplateTextParts

from Instructors.lupaQuestion import lupa_available, LupaQuestion, CodeSegment
from Students.models import StudentChallengeQuestions
from oneUp.settings import BASE_DIR

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


def basicqdict(question, i, challengeId, challenge_question, studChallQuest):
    qdict = makeSerializableCopyOfDjangoObjectqdictionary(question)
    qdict['challenge_question_id'] = challenge_question.pk
    qdict['id'] = question.questionID
    qdict['index'] = i
    correct_answers = [
        makeSerializableCopyOfDjangoObjectqdictionary(ca)
        for ca in CorrectAnswers.objects.filter(questionID=question.questionID)
    ]
    canswer_range = range(1, len(correct_answers) + 1)
    qdict['correct_answers'] = list(zip(canswer_range, correct_answers))

    # question_point = ChallengesQuestions.objects.get(pk=challenge_question.pk)
    qdict['point'] = challenge_question.points
    qdict['total_points'] = qdict['point']
    return qdict


def staticqdict(question, i, challengeId, challenge_question, studChallQuest):
    staticQuestion = StaticQuestions.objects.get(pk=question.questionID)
    qdict = basicqdict(staticQuestion, i, challengeId, challenge_question, studChallQuest)
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


def matchingqdict(question, i, challengeId, challenge_question, studChallQuest):
    qdict = staticqdict(question, i, challengeId, challenge_question, studChallQuest)
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
#Parsons1
# def parsonsqdict(question, i, challengeId, studChallQuest):
#     qdict = staticqdict(question, i, challengeId, studChallQuest)
#     modelSolution = Answers.objects.filter(questionID=question)
#     solution_string = modelSolution[0].answerText

#     #print("model solution", modelSolution)
#     qdict['languageName'] = re.search(
#         r'Language:([^;]+)', solution_string).group(1).lower().lstrip()
#     qdict['indentation'] = re.search(r';Indentation:([^;]+);',
#                                      solution_string).group(1)

#     languageAndLanguageName = re.search(r'Language:([^;]+)', solution_string)
#     intentationEnabledVariableAndValue = re.search(r';Indentation:([^;]+);',
#                                                    solution_string)
#     solution_string = solution_string.replace(
#         languageAndLanguageName.group(0), "")
#     solution_string = solution_string.replace(
#         intentationEnabledVariableAndValue.group(0), "")

#     qdict['answerText'] = solution_string
#     #print("solution String before changes",repr(solution_string))
#     #dynamically set dfficulty of parson distractor

#     #get the count of the distractors

#     distractorCount = len(
#         re.findall(r'(?=#dist)',
#                    repr(solution_string).strip('"\'')))
#     qdict['distractorCount'] = distractorCount

#     #set the count of distractors off the question's hardness
#     if (question.difficulty == "Easy"):
#         distractorCount = 0
#         distractorCount = int(distractorCount / 2)

#     qdict['distractorCount'] = distractorCount
#     #if the question difficulty is hard,
#     ##then we just use the full distractor count

#     #repr function will give us the raw representation of the string
#     #print("Solution String", repr(solution_string))
#     solution_string = re.sub("\t{3}", "☃            ", solution_string)
#     solution_string = re.sub("\t{2}", "☃        ", solution_string)
#     solution_string = re.sub("\t{1}", "☃    ", solution_string)

#     #tokenizer characters ☃ and ¬
#     solution_string = re.sub("\n", "\n¬☃", solution_string)
#     solution_string = re.sub("^[ ]+?", "☃", solution_string)
#     #print("Solution String", solution_string)

#     #we turn the student solution into a list
#     solution_string = re.sub("(?<=\n)\t*", "   ", solution_string)
#     solution_string = [x.strip() for x in solution_string.split('¬')]
#     #print("solutionString", solution_string)

#     #give each string the new line
#     tabedSolution_string = []

#     #indentation flag allows checking to see if next line should be indented
#     indentationFlag = 0
#     pattern = re.compile("##")
#     for line in solution_string:
#         originalLine = line
#         #we need the original line to match against when we find the next element
#         line = re.sub("☃", "", line)
#         if (indentationFlag == 1):
#             #if indentation flag is 1 then we know that on this line we must indent
#             indentationFlag = 0
#             line = re.sub("^ *", '&nbsp;' + ' ' * 4, line)
#         leadingSpacesCount = len(line) - len(line.lstrip(' '))
#         if (pattern.search(line) != None):
#             #get the net line, find out its spaces count
#             nextelem = solution_string[solution_string.index(originalLine) + 1]
#             nextelem = re.sub("☃", "", nextelem)
#             leadingSpacesCountNextLine = len(nextelem) - len(
#                 nextelem.lstrip(' '))

#             #we use the difference to calculate whether we must indent and where
#             difference = leadingSpacesCount - leadingSpacesCountNextLine
#             #print("Difference", difference)
#             if (difference == -4):
#                 #if indentation is after the line
#                 #ex:
#                 #data++;
#                 #   index++;
#                 indentationFlag = 1
#             if (difference == 4):
#                 #if indentation is before the line
#                 #ex:
#                 #   data++;
#                 #index++;
#                 modifier = int(leadingSpacesCount / 2)
#                 if (modifier > 1 and leadingSpacesCount == 8):
#                     #this modifier multiplies by the spaces count, if 8 then 4 in front, 4 after nbsp
#                     #this is a quirk of parsons.js
#                     line = re.sub("^ *", ' ' * modifier + '&nbsp;' + ' ' * 5,
#                                   line)
#                 else:
#                     line = re.sub("^ *", '&nbsp;' + ' ' * 4, line)
#         #print("line", repr(line))
#         line = re.sub("\t(?=return.*; *##)", "&nbsp;    ", line)
#         line = re.sub("(\s{4}|\t)(?=.* *##})", '&nbsp;' + ' ' * 4, line)
#         line = line + "\n"
#         tabedSolution_string.append(line)

#     solution_string = ""
#     solution_string = solution_string.join(tabedSolution_string)
#     qdict['solution_string'] = solution_string
#     qdict['tabbed_sol_string'] = tabedSolution_string
#     #print("tabbedSol String", tabedSolution_string)
#     #print("joinedSolString", repr(solution_string))

#     solution_string = re.sub("##\\n *", "\\\\n", solution_string)
#     solution_string = re.sub("\\\\n\t", "\\\\n", solution_string)
#     solution_string = re.sub("(?<=\n)\s{4}", "\t", solution_string)
#     qdict['model_solution'] = repr(solution_string).strip('\'')
#     #print("questqdict['model_solution']", qdict['model_solution'])

#     return qdict

def parsonsqdict(question, i, challengeId, challenge_question,studChallQuest):
    from Instructors.views import parsonsView
    qdict = staticqdict(question, i, challengeId, challenge_question, studChallQuest)
    modelSolution = Answers.objects.filter(questionID=question.questionID)
    solution_string = modelSolution[0].answerText

    qdict['languageName'] = parsonsView.findLanguage(solution_string)
    qdict['indentation_flag'] = parsonsView.findIndentation(solution_string)
    qdict['answerText'] = parsonsView.findAnswerText(solution_string)

    #determine if ther are tabs included
    tabLocator = re.compile("\t")
    if(tabLocator.search( qdict['answerText'])):
        qdict['answerText'] = parsonsView.convertTabsToSpaces(qdict['answerText'])

    qdict['distractor_limit'] = parsonsView.findDistractorLimit(solution_string, question)
    distractor_limit = qdict['distractor_limit']

    #tokenizer characters ☃ and ¬
    solution_string = re.sub("\n", "\n¬☃", qdict['answerText'])
    solution_string = [x.strip() for x in solution_string.split('¬')]
    qdict['answerText'] = solution_string

    model_solution = parsonsView.getModelSolution(solution_string, distractor_limit)
    qdict['model_solution'] = model_solution['model_solution']
    qdict['indentation'] = model_solution['indentation']

    #display code contains the code for displaying what the student selected
    qdict['display_code'] = model_solution['display_code']

    return qdict

def dynamicqdict(question, i, challengeId, challenge_question, studChallQuest):
    dynamicQuestion = DynamicQuestions.objects.get(pk=question.questionID)
    qdict = basicqdict(dynamicQuestion, i, challengeId, challenge_question, studChallQuest)
    if not lupa_available:
        qdict['questionText'] = "<B>Lupa not installed.  Please ask your server administrator to install it to enable dynamic problems.</B>"
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
        questionIdString = os.path.join(BASE_DIR, 'lua/problems/'+str(question.questionID)+'/')
        lupaQuest = LupaQuestion(code, libs, seed, str(i), numParts, questionIdString)

        #                            if (lupaQuest.error):
        #                                context_qdict['error']=lupaQuest.error
        #                                return render(request,'Instructors/DynamicQuestionAJAXResult.html',context_qdict)

        qdict['parts'] = dict()
        qdict['parts']["1"] = dict()
        for j in range(1,numParts+1):
            qdict['parts'][str(j)] = {'submissionCount':0} 
        qdict['parts']["1"]['questionText'] = lupaQuest.getQuestionPart(1)
        qdict['questionText'] = qdict['parts']["1"]['questionText']
        qdict['lupaquestion'] = lupaQuest.serialize()
        qdict['requestType'] = '_eval'
        if numParts > 1:
            qdict['hasMultipleParts'] = True
        else:
            qdict['hasMultipleParts'] = False
        qdict['uniqid']=i
        if TemplateDynamicQuestions.objects.filter(pk=question.pk).exists():
            qdict['dynamic_type'] = 'template'
            templateTextParts = TemplateTextParts.objects.filter(dynamicQuestion=question)
            for ttp in templateTextParts:
                qdict['parts'][str(ttp.partNumber)]['maxpoints'] = ttp.pointsInPart
        else:
            qdict['dynamic_type'] = 'raw_lua'
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
    qdict = addFeedback(qdict)
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
    qdict = addFeedback(qdict)
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
            # Get the user answer text based on the choice they selected (userAnswerIndex)
            answerText = [answers[1]['answerText'] for answers in qdict['answers_with_count'] if answers[0] == userAnswerIndex]
            userAnswers.append({
                'answerNumber':
                userAnswerIndex,
                'answerText': answerText[0]
                # This was getting the correct matching answer and not the user answer they selected
                # MatchingAnswers.objects.get(pk=parts[0]).answerID.answerText
            })
            if correctAnswerIndex == userAnswerIndex:
                userScore = userScore + valuePerAnswer

    qdict['user_points'] = round(userScore, 2)
    qdict['user_answers'] = userAnswers
    qdict = addFeedback(qdict)
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
        qdict = addFeedback(qdict)
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
    qdict = addFeedback(qdict)
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
            if value.startswith(indexstring + "-1-"):
                answers[value[len(indexstring) + 3:]] = POST[value]
        studentAnswerList = [
            key + ":" + answers[key] for key in answers.keys()
        ]
        storedAnswers=qdict["parts"]["1"]["user_answers"] if "parts" in qdict and "1" in qdict["parts"] and "user_answers" in qdict["parts"]["1"] else dict()
        studentAnswerList.extend([key + ":" + storedAnswers[key] for key in storedAnswers.keys()])
        return studentAnswerList
    else:
        studentAnswers = dict()
        submissionCount = dict()
        lastPartSubmitted = 0
        for pnum in qdict['parts']:
            if 'user_answers' in qdict['parts'][pnum]:
                user_answers=qdict['parts'][pnum]['user_answers']
            else:
                user_answers=dict()
            studentAnswers[pnum]=user_answers
            submissionCount[pnum]=qdict['parts'][pnum]['submissionCount']
            if submissionCount[pnum] > 0:
                lastPartSubmitted = max(lastPartSubmitted,int(pnum))
        return [json.dumps({'user_answers':studentAnswers,'lastPartSubmitted':lastPartSubmitted,'submissionCount':submissionCount})]

def dynamicAnswersAndGrades(qdict, studentAnswers):
    if lupa_available:
        from Instructors.views.dynamicQuestionView import rescale_evaluations
        if qdict['dynamic_type'] == 'template':
            ttp = TemplateTextParts.objects.filter(dynamicQuestion=qdict['id'])
        lupaQuestion = LupaQuestion.createFromDump(qdict['lupaquestion'])
        if qdict['numParts'] == 1:
            answers = {}
            for ans in studentAnswers:
                answerParts = ans.split(":")
                answers[answerParts[0]] = answerParts[1]
            qdict['user_answers'] = answers
            qdict['evaluations'] = lupaQuestion.answerQuestionPart(1, answers)
            if qdict['evaluations']:
                if qdict['dynamic_type'] == 'template':
                    maxpoints = ttp[0].pointsInPart
                else:
                    maxpoints = lupaQuestion.getPartMaxPoints(1)
                rescale_evaluations(qdict['evaluations'], qdict['total_points']/maxpoints)
                qdict['user_points'] = sum( [eval['value'] for eval in qdict['evaluations']] )
            else:
                qdict['user_points'] = 0
            qdict['sampleCorrect'] = lupaQuestion.getPartExampleAnswers(1)
        else:
            answersStruct = json.loads(studentAnswers[0])
            totalMaxPoints = 0
            for i in range(1,answersStruct['lastPartSubmitted']+1):
                stri = str(i)
                if 'questionText' not in qdict['parts'][stri]:
                    qdict['parts'][stri]['questionText'] = lupaQuestion.getQuestionPart(i)
                qdict['parts'][stri]['user_answers'] = answersStruct['user_answers'][stri]
                qdict['parts'][stri]['evaluations'] = lupaQuestion.answerQuestionPart(i,answersStruct['user_answers'][stri])
                qdict['parts'][stri]['sampleCorrect'] = lupaQuestion.getPartExampleAnswers(i)
            for i in range(1,qdict['numParts']+1):
                if qdict['dynamic_type'] == 'template':
                    maxpoints = ttp.get(partNumber=i).pointsInPart
                else:
                    maxpoints = lupaQuestion.getPartMaxPoints(i)
                totalMaxPoints += maxpoints
            user_points = 0
            for i in range(1,answersStruct['lastPartSubmitted']+1):
                stri =str(i)              
                submissionCount = answersStruct['submissionCount'][stri]
                qdict['parts'][stri]['submissionCount']=submissionCount
                from Instructors.views.dynamicQuestionView import calcResubmissionPenalty
                resubpenalty = calcResubmissionPenalty(submissionCount-1,qdict)
                tp = qdict['total_points']
                sf = qdict['total_points']/totalMaxPoints*resubpenalty
                rescale_evaluations(qdict['parts'][stri]['evaluations'], qdict['total_points']/totalMaxPoints*resubpenalty)
                user_points += sum( [eval['value'] for eval in qdict['parts'][stri]['evaluations']] )
            qdict['user_points'] = user_points
    return qdict

def modifyQDictForView(qdict):
    print("printing")
    templateDynamicQuestion = TemplateDynamicQuestions.objects.filter(questionID=qdict['questionID'])
    result = "<b>Templated set up code: </b><br><br>"
    result += '<p>' + templateDynamicQuestion.first().setupCode + '</p><br>'
    index = 1
    for part in qdict['parts']:
        templateTextPart = TemplateTextParts.objects.get(partNumber=part ,dynamicQuestion=qdict['questionID'])
        result += '<p> Part: ' + str(index) + "</p>"
        result += '<p> '+ templateTextPart.templateText + '</p><br>'
        index += 1
            
    qdict['questionText'] = result
    qdict['hasMultipleParts'] = False
    qdict['submissionsAllowed'] = 0
    return qdict

def parsonsMakeAnswerList(qdict, POST):
    from Instructors.views import parsonsView
    import json, ast
    
    student_answers = {}
    student_solution_JSON = json.loads(POST[str(qdict['index']) + 'studentSol'])
    student_trash_JSON = json.loads(POST[str(qdict['index']) + 'studentTrash'])

    student_answers = parsonsView.generateStudentSolution(student_solution_JSON, student_trash_JSON, qdict['display_code'])
    student_answers['feedback_button_click_count'] = int(POST[str(qdict['index']) + 'feedBackButtonClickCount'])

    student_answers['correct_line_count'] = parsonsView.getCorrectCount(
            student_answers['student_hashes'], 
            qdict['display_code']
        )

    student_answers['indentation_errors'] = parsonsView.getIndenationErrorCount(
            student_answers['student_indentation'], 
            qdict['indentation']
        )
    return [json.dumps(student_answers)]


def parsonsAddAnswersAndGrades(qdict, studentAnswers):
    from Instructors.views import parsonsView
    import ast
    qdict = parsonsCorrectAnswers(qdict)

    answer = Answers.objects.filter(questionID=qdict['questionID'])
    answer = answer[0].answerText
    studentAnswerDict = ast.literal_eval(studentAnswers[0])
    correctLineCount = int (studentAnswerDict['correct_line_count'])
    wrongPositionLineNumbers = studentAnswerDict['indentation_errors']
    
    qdict['user_points'] = parsonsView.gradeParson(qdict, studentAnswerDict)
    qdict['student_solution'] = studentAnswerDict['student_solution_string']
    qdict = addFeedback(qdict)
    return qdict

def parsonsCorrectAnswers(qdict):
    answer = Answers.objects.filter(questionID=qdict['questionID'])
    answer = answer[0].answerText
    #print("Model Solution: ", answer)

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

def addFeedback(qdict):
    static_question = StaticQuestions.objects.get(questionID=qdict['questionID'])
    if qdict['user_points'] == qdict['total_points']:
        qdict['feedback'] = static_question.correctAnswerFeedback
    else:
        qdict['feedback'] = static_question.incorrectAnswerFeedback
    return qdict

questionTypeFunctions = {
    QuestionTypes.multipleChoice: {
        "makeqdict": staticqdict,
        "makeAnswerList": multipleChoiceMakeAnswerList,
        "studentAnswersAndGrades": multipleChoiceAnswersAndGrades,
        "correctAnswers": multipleChoiceCorrectAnswers,
         "modifyQdictForView": lambda qdict: qdict,
    },
    QuestionTypes.multipleAnswers: {
        "makeqdict": staticqdict,
        "makeAnswerList": multipleAnswerMakeAnswerList,
        "studentAnswersAndGrades": multipleAnswerAddAnswersAndGrades,
        "correctAnswers": multipleAnswerCorrectAnswers,
         "modifyQdictForView": lambda qdict: qdict,
    },
    QuestionTypes.matching: {
        "makeqdict": matchingqdict,
        "makeAnswerList": matchingMakeAnswerList,
        "studentAnswersAndGrades": matchingAddAnswersAndGrades,
        "correctAnswers": lambda qdict: qdict,  # Already done in makeqdict
        "modifyQdictForView": lambda qdict: qdict,
    },
    QuestionTypes.trueFalse: {
        "makeqdict": staticqdict,
        "makeAnswerList": trueFalseMakeAnswerList,
        "studentAnswersAndGrades": trueFalseAddAnswersAndGrades,
        "correctAnswers": trueFalseCorrectAnswers,
        "modifyQdictForView": lambda qdict: qdict,
    },
    QuestionTypes.essay: {
        "makeqdict": basicqdict,
        "makeAnswerList": lambda qdict, POST: [],
        "studentAnswersAndGrades": lambda qdict, studentAnswers: qdict,
        "correctAnswers": lambda qdict: qdict,
        "modifyQdictForView": lambda qdict: qdict,
    },
    QuestionTypes.dynamic: {
        "makeqdict": dynamicqdict,
        "makeAnswerList": dynamicMakeAnswerList,
        "studentAnswersAndGrades": dynamicAnswersAndGrades,
        "correctAnswers": lambda qdict: qdict,
        "modifyQdictForView": lambda qdict: qdict,
    },
    QuestionTypes.templatedynamic: {
        "makeqdict": dynamicqdict,
        "makeAnswerList": dynamicMakeAnswerList,
        "studentAnswersAndGrades": dynamicAnswersAndGrades,
        "correctAnswers": lambda qdict: qdict,
        "modifyQdictForView": modifyQDictForView,
    },
    QuestionTypes.parsons: {
        "makeqdict": parsonsqdict,
        "makeAnswerList": parsonsMakeAnswerList,
        "studentAnswersAndGrades": parsonsAddAnswersAndGrades,
        "correctAnswers": parsonsCorrectAnswers,
        "modifyQdictForView": lambda qdict: qdict,
    },
}
