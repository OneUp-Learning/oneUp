#
# Created  updated 05/30/2018
# DD
#

from django.shortcuts import render, redirect

from Instructors.models import StaticQuestions, Answers, CorrectAnswers
from Instructors.models import Challenges, ChallengesQuestions

from Instructors.views.utils import initialContextDict, getCourseSkills, addSkillsToQuestion, saveTags, getSkillsForQuestion, extractTags, utcDate
from Badges.enums import QuestionTypes, ObjectTypes
from Instructors.constants import unassigned_problems_challenge_name, default_time_str


from django.contrib.auth.decorators import login_required
from decimal import Decimal

from oneUp.logger import logger

@login_required
def parsonsForm(request):
    context_dict, currentCourse = initialContextDict(request)

    # In this class, these are the names of the attributes which are strings.
    # We put them in an array so that we can copy them from one item to
    # another programmatically instead of listing them out.
    string_attributes = ['preview','questionText','difficulty','correctAnswerFeedback',
                  'incorrectAnswerFeedback','instructorNotes','author'];

    if 'view' in request.GET:
        context_dict['view'] = 1
             
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
        question.type = QuestionTypes.parsons
        
        if question.author == '':
            question.author = request.user.username
        
        question.save();  
        
        # Save the entered model solution as "correctAnswer"        
        answers = Answers.objects.filter(questionID=question)
        if answers:
            answer = answers[0]
            answer.answerText = request.POST['setupCode']
            print("Answer:", answer.answerText)
            answer.save()
            # no need to change correct answer
            #correctAnswerObject = CorrectAnswers.objects.filter(questionID=question)
        else:
            answer = Answers()         
            answer.questionID = question
           # answer.answerText = request.POST['setupCode']
            
            #GGM
            aceInput = request.POST['setupCode']
            print("Answer ", answer.answerText)
            #proces the input
            
            answer.answerText = aceInput
            answer.save()
            # the answer is also the correct answer - model solution to be displayed to the student
            correctAnswerObject = CorrectAnswers()
            correctAnswerObject.questionID = question           
            correctAnswerObject.answerID = answer
            correctAnswerObject.save()

       
        # Processing and saving tags in DB
        saveTags(request.POST['tags'], question, ObjectTypes.question)
        
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
        
            ChallengesQuestions.addQuestionToChallenge(question, challenge, Decimal(request.POST['points']), position)

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
        challenge.startTimestamp = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
        challenge.endTimestamp = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
        challenge.numberAttempts = 99999
        challenge.timeLimit = 99999
        challenge.save()
        ChallengesQuestions.addQuestionToChallenge(question, challenge, 0, 0)
        
        redirectVar = redirect('/oneUp/instructors/challengeQuestionsList?problems', context_dict)
        return redirectVar

    elif request.method == 'GET':
            
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
            
            # Copy all of the attribute values into the context_dict to display them on the page.
            context_dict['questionId']=request.GET['questionId']
            for attr in string_attributes:
                context_dict[attr]=getattr(question,attr)

            # Load the model solution, which is stored in Answers
            answer = Answers.objects.filter(questionID=question)
            context_dict['model_solution'] = answer[0].answerText
            
 
            # Extract the tags from DB            
            context_dict['tags'] = extractTags(question, "question")
            
            if 'challengeID' in request.GET:
                # get the challenge points for this problem to display
                challenge_questions = ChallengesQuestions.objects.filter(challengeID=request.GET['challengeID']).filter(questionID=request.GET['questionId'])
                context_dict['points'] = challenge_questions[0].points
                
                # set default skill points - 1
                context_dict['q_skill_points'] = int('1')

                # Extract the skill                                        
                context_dict['selectedSkills'] = getSkillsForQuestion(currentCourse,question)                    

        if 'questionId' in request.POST:         
            return redirect('challengesView')
    
    return render(request,'Instructors/ParsonsForm.html', context_dict)
