#
#  Updated 01/29/2016
#  Last updated 07/14/2017
#

from django.shortcuts import render
from django.shortcuts import redirect

from Instructors.models import StaticQuestions, Answers, MatchingAnswers, CorrectAnswers
from Instructors.models import Challenges, ChallengesQuestions
from Instructors.constants import unassigned_problems_challenge_name, default_time_str, unlimited_constant

from Instructors.views.utils import initialContextDict, getCourseSkills, addSkillsToQuestion, saveTags, getSkillsForQuestion, extractTags, utcDate
from Badges.enums import ObjectTypes
from Instructors.questionTypes import QuestionTypes

from django.contrib.auth.decorators import login_required, user_passes_test
from oneUp.logger import logger
from decimal import Decimal
from oneUp.decorators import instructorsCheck  
from oneUp.ckeditorUtil import config_ck_editor

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')   
def matchingForm(request):
    context_dict, currentCourse = initialContextDict(request)


    # In this class, these are the names of the attributes which are strings.
    # We put them in an array so that we can copy them from one item to
    # another programmatically instead of listing them out.
    string_attributes = ['preview','questionText','difficulty','correctAnswerFeedback',
                  'incorrectAnswerFeedback','instructorNotes','author']

    # We set these structures up here for later use.
    
    if 'view' in request.GET:
        context_dict['view'] = 1
        
    # Flag to indicate whether or not ansValue, ansPK, and ansChecked have been
    # filled in.
    answersSet = False
    ansValue = []      #Text for existing answers
    ansPK = []         #PK for existing answers
    ansChecked = []    #Whether or not existing answer is the correct one.
    matchText = []     #Text for existing matching answers

    context_dict['skills'] = getCourseSkills(currentCourse)
    context_dict['tags'] = []
    if request.method == 'POST':
        # If there's an existing question, we wish to edit it.  If new question,
        # create a new Question object.
        if 'questionId' in request.POST:
            qi = request.POST['questionId']
            if not qi == "":                                         
                print('questionId '+request.POST['questionId'])
                question = StaticQuestions.objects.get(pk=int(qi))
            else:
                question = StaticQuestions()
        else:
            question = StaticQuestions()

        # Copy all strings from POST to database object.
        for attr in string_attributes:
            setattr(question,attr,request.POST[attr])
        
        # Fix the question type
        question.type = QuestionTypes.matching

        
        if question.author == '':
            question.author = request.user.username
            
        question.save()  #Writes to database.
          

        # The number of answers is always sent.
        num_answers = int(request.POST['numAnswers'])
        
        answers = set()
        mAnswers = set()

        # For each answer returned
        for x in range(1,num_answers+1):
            # If PK is returned, we fetch from the database
            if request.POST['ansPK'+str(x)]:
                answer = Answers.objects.get(pk=int(request.POST['ansPK'+str(x)]))
                answer.answerText = request.POST['answer'+str(x)]
                answer.save()
                answers.add(answer)
            else:
                answer = Answers()
                answer.questionID = question
                answer.answerText = request.POST['answer'+str(x)]
                
            if (answer.answerText): # Save only if there is text.
                answer.save()
                answers.add(answer)
 
            mAnswer = MatchingAnswers()
            mAnswer.answerID = answer
            mAnswer.matchingAnswerText = request.POST['matchingAnswer'+str(x)]
            mAnswer.questionID = question
            if (mAnswer.matchingAnswerText): # Save only if there is text.
                mAnswer.save()
                mAnswers.add(mAnswer)

        # Note: in current version if the user selects a blank field as
        # the correct answer, errors may result.
        
        # Get the answers currently in the database
        existingAnswers = Answers.objects.filter(questionID=question)
        # Check them to make sure we didn't delete them this time around.
        for existingAnswer in existingAnswers:
            if existingAnswer not in answers:
                existingAnswer.delete()
                                
        # Same for the matching answers
        # Get the matching answers currently in the database
        existingMatchAnswers = MatchingAnswers.objects.filter(questionID=question)
        for existingMatchAnswer in existingMatchAnswers:
            if existingMatchAnswer not in mAnswers:
                existingMatchAnswer.delete()
                
        # Processing and saving tags in DB                        
        saveTags(request.POST['tags'], question, ObjectTypes.question)
        
        # Call made from the Challenge page: must include points  for the question for this challenge
        if 'challengeID' in request.POST:
            # save in ChallengesQuestions if not already saved            
  
            position = ChallengesQuestions.objects.filter(challengeID=request.POST['challengeID']).count() + 1
            
            positions = []
            if  'questionId' in request.POST:      
                # Delete challenge question (even duplicates)                     
                challenge_questions = ChallengesQuestions.objects.filter(challengeID=request.POST['challengeID']).filter(questionID=request.POST['questionId'])
                for chall_question in challenge_questions:
                    positions.append((chall_question.pk, chall_question.questionPosition, chall_question.points))
                
                challenge_questions.delete()

            challengeID = request.POST['challengeID']
            challenge = Challenges.objects.get(pk=int(challengeID))
            if positions:
                # Recreate challenge question (and duplicates)
                for pk, pos, points in positions:
                    if pk == int(request.POST['challengeQuestionID']):
                        points = Decimal(request.POST['points'])
                    ChallengesQuestions.addQuestionToChallenge(question, challenge, points, pos)
            else:
                ChallengesQuestions.addQuestionToChallenge(question, challenge, Decimal(request.POST['points']), position)
                    
            # Processing and saving skills for the question in DB
            addSkillsToQuestion(currentCourse,question,request.POST.getlist('skills[]'),request.POST.getlist('skillPoints[]'))
                                  
            redirectVar = redirect('/oneUp/instructors/challengeQuestionsList', context_dict)
            redirectVar['Location']+= '?challengeID='+request.POST['challengeID']
            return redirectVar
        
        # Question is unassigned so create unassigned challenge object
        challenge = Challenges()
        challenge.challengeName = unassigned_problems_challenge_name
        challenge.courseID = currentCourse
        challenge.startTimestamp = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
        challenge.endTimestamp = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
        challenge.numberAttempts = unlimited_constant
        challenge.timeLimit = unlimited_constant
        challenge.save()
        ChallengesQuestions.addQuestionToChallenge(question, challenge, 0, 0)
        
        redirectVar = redirect('/oneUp/instructors/challengeQuestionsList?problems', context_dict) 
        return redirectVar
                
    # request.GET                
    elif request.method == 'GET':
        num_answers = 4 #default number of blanks for new questions            
        if Challenges.objects.filter(challengeID = request.GET['challengeID'],challengeName=unassigned_problems_challenge_name):
            context_dict["unassign"]= 1
            
        if 'challengeQuestionID' in request.GET:
            context_dict['challengeQuestionID'] = request.GET['challengeQuestionID']

        if 'challengeID' in request.GET:
            context_dict['challengeID'] = request.GET['challengeID']
            chall = Challenges.objects.get(pk=int(request.GET['challengeID']))
            context_dict['challengeName'] = chall.challengeName
            context_dict['challenge'] = True
            context_dict['tags'] = []

        # In case we specify a different number of blanks
        if 'num_answers' in request.GET:
            num_answers = request.GET['num_answers']
            
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
            for answer in answers:
                matchingAnswer = MatchingAnswers.objects.filter(answerID = answer)
                
                # Set up the arrays
                matchText.append(matchingAnswer[0].matchingAnswerText)
                ansValue.append(answer.answerText)
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
                # get the points to display
                if 'challengeQuestionID' in request.GET:
                    challenge_questions = ChallengesQuestions.objects.filter(pk=int(request.GET['challengeQuestionID']))
                    context_dict['points'] = challenge_questions[0].points
                else:
                    context_dict['points'] = 0
                
                # set default skill points - 1                              
                context_dict['q_skill_points'] = int('1')

                # Extract the skill                                        
                context_dict['selectedSkills'] = getSkillsForQuestion(currentCourse,question)                    
                logger.debug('[GET] challengeID  '+request.GET['challengeID'])
                    
    # If we didn't run that code to load the values for the answers, then we make
    # blank lists.  We do this because we need to use a zipped list and a for
    # in order for the template stuff to be happy with us.  Doing that requires that
    # all the lists have the same length
    if not answersSet:
        for i in range(0,num_answers):
            ansValue.append("")
            ansPK.append("")
            ansChecked.append("")
            matchText.append("")  

    context_dict['num_answers'] = num_answers
    # The range part is the index numbers.
    context_dict['answer_range'] = zip(range(1,num_answers+1),ansValue,ansPK,ansChecked,matchText)
    
    if 'questionId' in request.POST:         
        return redirect('challengesView')

    context_dict['ckeditor'] = config_ck_editor()

    return render(request,'Instructors/MatchingForm.html', context_dict)