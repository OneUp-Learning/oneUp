#
# Last updated 01/29/2016
# Last updated 07/14/2017
#

from decimal import Decimal

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render

from Badges.enums import ObjectTypes
from Instructors.constants import (unassigned_problems_challenge_name,
                                   unlimited_constant)
from Instructors.models import (Answers, Challenges, ChallengesQuestions,
                                CorrectAnswers, StaticQuestions)
from Instructors.questionTypes import QuestionTypes
from Instructors.views.utils import (addSkillsToQuestion, extractTags,
                                     getCourseSkills, getSkillsForQuestion,
                                     initialContextDict, saveTags,
                                     update_or_create_challenge_questions)
from oneUp.ckeditorUtil import config_ck_editor
from oneUp.decorators import instructorsCheck
from oneUp.logger import logger


@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')   
def trueFalseNewForm(request):
    context_dict, currentCourse = initialContextDict(request)

    # In this class, these are the names of the attributes which are strings.
    # We put them in an array so that we can copy them from one item to
    # another programmatically instead of listing them out.
    string_attributes = ['preview','questionText','difficulty','correctAnswerFeedback',
                  'incorrectAnswerFeedback','instructorNotes','author'];
    bool_values = ['true', 'false']

    if 'view' in request.GET:
        context_dict['view'] = 1
            
    # We set these structures up here for later use.

    # Flag to indicate whether or not ansValue, ansPK, and ansChecked have been
    # filled in.
    answersSet = False
    ansValue = []      #Text for existing answers
    ansPK = []         #PK for existing answers
    ansChecked = []    #Whether or not existing answer is the correct one.
    num_answers = 2    #'true' and 'false'
    
    context_dict['skills'] = getCourseSkills(currentCourse)
    context_dict['tags'] = []
    if request.method == 'POST':

        # If there's an existing question, we wish to edit it.  If new question,
        # create a new Question object.
        if 'questionId' in request.POST:
            qi = request.POST['questionId']
            if not qi == "":
                logger.debug('questionId '+request.POST['questionId'])
                question = StaticQuestions.objects.get(pk=int(qi))
            else:
                question = StaticQuestions()
        else:
            question = StaticQuestions()

        # Copy all strings from POST to database object.
        for attr in string_attributes:
            setattr(question,attr,request.POST[attr])
        
        # Fix the question type
        question.type = QuestionTypes.trueFalse
        
        if question.author == '':
            question.author = request.user.username

        if 'strongHint' in request.POST:
            question.strongHint = request.POST['strongHint']
        if 'basicHint' in request.POST:
            question.basicHint = request.POST['basicHint']
        question.isHintUsed = "hintUsed" in request.POST
        question.save();  
        
        # The index of the correct answer.
        if 'correctAnswer' in request.POST:
            correct_answer = int(request.POST['correctAnswer'])
        else:
            correct_answer = 1   # true by default ?????

        answers = set()
        # For each answer ('true', 'false')
        for x in range(1, num_answers + 1):

            # If PK is returned, we fetch from the database
            if 'ansPK'+str(x) in request.POST and request.POST['ansPK'+str(x)] != '':
                answer = Answers.objects.get(pk=int(request.POST['ansPK'+str(x)]))
                answer.answerText = bool_values[x-1] # answers are always 'true' and 'false'
                answer.save()
                answers.add(answer)
            else:
                # Otherwise, we create new answers 'true' and 'false'
                answer = Answers()
                answer.questionID = question
                answer.answerText = bool_values[x-1]
                answer.save()
                answers.add(answer)

            # Note: in current version if the user selects a blank field as
            # the correct answer, errors may result.
            if x == correct_answer:

                # Load any existing records of which answer is correct and delete them
                existingCorrectAnswers = CorrectAnswers.objects.filter(questionID=question)
                for existingCorrectAnswer in existingCorrectAnswers:
                    existingCorrectAnswer.delete()

                # Create and save a new correct answer entry
                correctAnswerObject = CorrectAnswers()
                correctAnswerObject.questionID = question
                correctAnswerObject.answerID = answer
                correctAnswerObject.save()
        
        # Processing and saving tags in DB
        saveTags(request.POST['tags'], question, ObjectTypes.question)
        
        if 'challengeID' in request.POST:
            # save in ChallengesQuestions if not already saved        # 02/28/2015    
            update_or_create_challenge_questions(request,question)
 
            # Processing and saving skills for the question in DB
            addSkillsToQuestion(currentCourse,question,request.POST.getlist('skills[]'),request.POST.getlist('skillPoints[]'))
    
            # Processing and saving tags in DB
            
            saveTags(request.POST['tags'], question, ObjectTypes.question)
                
                
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
            
        if 'challengeQuestionID' in request.GET:
            context_dict['challengeQuestionID'] = request.GET['challengeQuestionID']

        if 'challengeID' in request.GET:
            context_dict['challengeID'] = request.GET['challengeID']
            chall = Challenges.objects.get(pk=int(request.GET['challengeID']))
            context_dict['challengeName'] = chall.challengeName
            context_dict['challenge'] = True
            context_dict['tags'] = []
            
            if Challenges.objects.filter(challengeID = request.GET['challengeID'],challengeName=unassigned_problems_challenge_name):
                context_dict["unassign"]= 1
            
        # If questionId is specified then we load for editing.
        if 'questionId' in request.GET:
            question = StaticQuestions.objects.get(pk=int(request.GET['questionId']))
            
            # Copy all of the attribute values into the context_dict to
            # display them on the page.
            context_dict['questionId']=request.GET['questionId']
            for attr in string_attributes:
                context_dict[attr]=getattr(question,attr)

            # Load the correct answers.  Should only be 0 or 1
            correctAnswers = CorrectAnswers.objects.filter(questionID=question)
            
            # Fetch the answers for this question from the database.
            answers = Answers.objects.filter(questionID=question)
            # Count them
            num_answers = len(answers)

            # We're going to go through the list twice.  Hopefully we only have two answers,
            # but, just in case, we've still got a list.
            # The first time we'll add the true answer (or answers) to the list
            # The second time, the false answer (or answers).
            for answer in answers:
                if answer.answerText == "true":
                    # Set up the arrays
                    ansValue.append(answer.answerText.capitalize())
                    ansPK.append(answer.answerID)
                    checked = False #element must be completely omitted for not checked
                    for correctAnswer in correctAnswers:
                        if correctAnswer.answerID == answer:
                            checked = True
                    ansChecked.append(checked)
            for answer in answers:
                if answer.answerText != "true":  # Hopefully this will just be false, but who knows.
                    # Set up the arrays
                    ansValue.append(answer.answerText.capitalize())
                    ansPK.append(answer.answerID)
                    checked = False #element must be completely omitted for not checked
                    for correctAnswer in correctAnswers:
                        if correctAnswer.answerID == answer:
                            checked = True
                    ansChecked.append(checked)
            answersSet = True

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
                context_dict['selectedSkills'] = getSkillsForQuestion(currentCourse,question)                    
            context_dict['basicHint'] = question.basicHint
            context_dict['strongHint'] = question.strongHint
            context_dict['hintUsed'] = question.isHintUsed
                            
    # If we didn't run that code to load the values for the answers, then we make
    # blank lists.  We do this because we need to use a zipped list and a for
    # in order for the template stuff to be happy with us.  Doing that requires that
    # all the lists have the same length
        if not answersSet:
            ansValue.append("True")
            ansPK.append("")
            ansChecked.append(True)
            ansValue.append("False")
            ansPK.append("")
            ansChecked.append(False)
    
        context_dict['num_answers'] = num_answers
        # The range part is the index numbers.
        context_dict['answer_range'] = zip(range(1,num_answers+1),ansValue,ansPK,ansChecked)
        if 'questionId' in request.POST:         
            return redirect('challengesView')
            
        context_dict['ckeditor'] = config_ck_editor()
    
    return render(request,'Instructors/TrueFalseForm.html', context_dict)
