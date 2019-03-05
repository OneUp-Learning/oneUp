#
# Last updated 03/24/2015
# Last updated 07/14/2017
#

from django.shortcuts import render
from django.shortcuts import redirect

from Instructors.models import StaticQuestions, Answers, CorrectAnswers, Challenges, ChallengesQuestions

from Instructors.views.utils import initialContextDict, getCourseSkills, addSkillsToQuestion, saveTags, getSkillsForQuestion, extractTags, utcDate
from Badges.enums import ObjectTypes
from Instructors.questionTypes import QuestionTypes

from decimal import Decimal

from Instructors.constants import default_time_str, unassigned_problems_challenge_name, unlimited_constant

from django.contrib.auth.decorators import login_required, user_passes_test
from oneUp.logger import logger
from oneUp.decorators import instructorsCheck   

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def multipleAnswersForm(request):
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
        question.type = QuestionTypes.multipleAnswers
        
        if question.author == '':
            question.author = request.user.username
            
        question.save()  #Writes to database.
          
        # The number of answers is always sent.
        num_answers = int(request.POST['numAnswers'])
                
        # empty set
        answers = set()
        
        # get the list of all checked answers
        correctAnswers = request.POST.getlist('correctAnswer')
        # Load any existing records of which answer is correct and delete them
        existingCorrectAnswers = CorrectAnswers.objects.filter(questionID=question);
        for existingCorrectAnswer in existingCorrectAnswers:
            existingCorrectAnswer.delete()

        # For each answer returned
        for x in range(1,num_answers+1):

            # If PK is returned, we fetch from the database
            if request.POST['ansPK'+str(x)]:
                answer = Answers.objects.get(pk=int(request.POST['ansPK'+str(x)]))
                answer.answerText = request.POST['answer'+str(x)]
                answer.save()
                answers.add(answer)
            else:
                # Otherwise, we create new.
                answer = Answers()
                answer.questionID = question
                answer.answerText = request.POST['answer'+str(x)]

                if (answer.answerText): # Save only if there is text.
                    answer.save()
                    answers.add(answer)
                else:
                    answer.save()

            # Note: in current version if the user selects a blank field as
            # the correct answer, errors may result.
            
            if str(x) in correctAnswers:
                # Create and save a new correct answer entry
                correctAnswerObject = CorrectAnswers()
                correctAnswerObject.questionID = question
                correctAnswerObject.answerID = answer
                correctAnswerObject.save()

        # Get the answers currently in the database
        existingAnswers = Answers.objects.filter(questionID=question)
        # Check them to make sure we didn't delete them this time around.
        for existingAnswer in existingAnswers:
            if existingAnswer not in answers:
                existingAnswer.delete()
        
        # Processing and saving tags in DB                        
        saveTags(request.POST['tags'], question, ObjectTypes.question)
        
        if 'challengeID' in request.POST:
            # save in ChallengesQuestions if not already saved        # 02/28/2015    
  
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
        
    #####################        
    # request.GET     
    elif request.method == 'GET':
        num_answers = 4 #default number of blanks for new questions
        
            
        if 'challengeID' in request.GET:
            context_dict['challengeID'] = request.GET['challengeID']
            chall = Challenges.objects.get(pk=int(request.GET['challengeID']))
            context_dict['challengeName'] = chall.challengeName
            context_dict['challenge'] = True
            context_dict['tags'] = []
            if Challenges.objects.filter(challengeID = request.GET['challengeID'],challengeName=unassigned_problems_challenge_name):
                context_dict["unassign"]= 1

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
                # Set up the arrays
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
                challenge_questions = ChallengesQuestions.objects.filter(challengeID=request.GET['challengeID']).filter(questionID=request.GET['questionId'])
                context_dict['points'] = challenge_questions[0].points
                
                # set default skill points - 1                             # 03/17/2015 
                context_dict['q_skill_points'] = int('1')
                
                # Extract the skill                                        
                context_dict['selectedSkills'] = getSkillsForQuestion(currentCourse,question)                    
                
                logger.debug('[GET] challengeID  '+request.GET['challengeID'])  
                
        # If we didn't run that code to load the values for the answers, then we make
        # blank lists.  We do this because we need to use a zipped list and a for
        # in order for the template stuff to be happy with us.  Doing that requires tha
        # all the lists have the same length
        if not answersSet:
            for i in range(0,num_answers):
                ansValue.append("")
                ansPK.append("")
                ansChecked.append("")

        context_dict['num_answers'] = num_answers
        # The range part is the index numbers.
        context_dict['answer_range'] = zip(range(1,num_answers+1),ansValue,ansPK,ansChecked)

        if 'questionId' in request.POST:         
            return redirect('challengesView')

        context_dict['ckeditor'] = config_ck_editor()

    return render(request,'Instructors/MultipleAnswersForm.html', context_dict)

DEFAULT_CONFIG = {
    'skin': 'moono-lisa',
    'toolbar_Basic': [
        ['Source', '-', 'Bold', 'Italic']
    ],
    'toolbar_Full': [
        ['Styles', 'Format', 'Bold', 'Italic', 'Underline', 'Strike', 'SpellChecker', 'Undo', 'Redo'],
        ['Link', 'Unlink', 'Anchor'],
        ['Image', 'Flash', 'Table', 'HorizontalRule'],
        ['TextColor', 'BGColor'],
        ['Smiley', 'SpecialChar'], ['Source'],
    ],
    'toolbar': 'Full',
    'height': 291,
    'width': 835,
    'filebrowserWindowWidth': 940,
    'filebrowserWindowHeight': 725,
}

def config_ck_editor(value='', config_name='default', extra_plugins=None, external_plugin_resources=None):
    from django.conf import settings
    from django.core.exceptions import ImproperlyConfigured
    from django.utils.translation import get_language
    from django.utils.encoding import force_text
    from django.utils.functional import Promise
    from django.utils.html import conditional_escape
    from django.utils.safestring import mark_safe
    from ckeditor.widgets import LazyEncoder
    from django.urls import reverse

    json_encode = LazyEncoder().encode

    config = DEFAULT_CONFIG.copy()
    # Try to get valid config from settings.
    configs = getattr(settings, 'CKEDITOR_CONFIGS', None)
    if configs:
        if isinstance(configs, dict):
            # Make sure the config_name exists.
            if config_name in configs:
                con = configs[config_name]
                # Make sure the configuration is a dictionary.
                if not isinstance(con, dict):
                    raise ImproperlyConfigured('CKEDITOR_CONFIGS["%s"] \
                            setting must be a dictionary type.' %
                                                config_name)
                # Override defaults with settings config.
                config.update(con)
            else:
                raise ImproperlyConfigured("No configuration named '%s' \
                        found in your CKEDITOR_CONFIGS setting." %
                                            config_name)
        else:
            raise ImproperlyConfigured('CKEDITOR_CONFIGS setting must be a\
                    dictionary type.')
    extra_plugins = extra_plugins or []

    if extra_plugins:
        config['extraPlugins'] = ','.join(extra_plugins)

    external_plugin_resources = external_plugin_resources or []
    external_plugin_resources = [[force_text(a), force_text(b), force_text(c)]
                                     for a, b, c in external_plugin_resources]

    if 'filebrowserUploadUrl' not in config:
        config.setdefault('filebrowserUploadUrl', reverse('ckeditor_upload'))
    if 'filebrowserBrowseUrl' not in config:
        config.setdefault('filebrowserBrowseUrl', reverse('ckeditor_browse'))

    lang = get_language()
    if lang == 'zh-hans':
        lang = 'zh-cn'
    elif lang == 'zh-hant':
        lang = 'zh'
    config['language'] = lang

    return {'value': conditional_escape(force_text(value)),
            'config': json_encode(config),
            'external_plugin_resources': json_encode(external_plugin_resources)
            }
