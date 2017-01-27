#
# Last updated 03/24/2015
#

from django.template import RequestContext
from django.shortcuts import render
from django.shortcuts import redirect

from Instructors.models import Questions, StaticQuestions, Answers, CorrectAnswers, Courses, CoursesSkills
from Instructors.models import Skills, QuestionsSkills, Challenges, ChallengesQuestions

from Instructors.views import utils
from Instructors.views.challengeListView import makeContextDictForQuestionsInChallenge
from Badges.enums import QuestionTypes

from django.contrib.auth.decorators import login_required

#MultipleChoiceQuestionType = QuestionTypes.objects.get(pk=1)


@login_required
def multipleChoiceForm(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict = { }
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username

    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected'

    # In this class, these are the names of the attributes which are strings.
    # We put them in an array so that we can copy them from one item to
    # another programmatically instead of listing them out.
    string_attributes = ['preview','questionText','difficulty','correctAnswerFeedback', # 04/09
                  'incorrectAnswerFeedback','instructorNotes'];

    # We set these structures up here for later use.
    
    if 'view' in request.GET:
        context_dict['view'] = 1
        
    # Flag to indicate whether or not ansValue, ansPK, and ansChecked have been
    # filled in.
    answersSet = False
    ansValue = []      #Text for existing answers
    ansPK = []         #PK for existing answers
    ansChecked = []    #Whether or not existing answer is the correct one.
    
    skill_ID = []
    skill_Name = []

    # Fetch the skills for this course from the database.
    course_skills = CoursesSkills.objects.filter(courseID=currentCourse)
         
    for s in course_skills:
        skill_ID.append(s.skillID.skillID)
        skill_Name.append(s.skillID.skillName)
    
    # The range part is the index numbers.
    context_dict['skill_range'] = zip(range(1,course_skills.count()+1),skill_ID,skill_Name)   

    if request.POST:
        # If there's an existing question, we wish to edit it.  If new question,
        # create a new Question object.
        if 'questionId' in request.POST:
            qi = request.POST['questionId']
            if not qi == "":                                         # 03/17/2015
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
        question.type = QuestionTypes.multipleChoice;
        
        # get the author                            # 03/10/2015
        if request.user.is_authenticated():
            question.author = request.user.username
        else:
            question.author = ""
        #question.author = "admin" 
        question.save();  #Writes to database.
        
        # The number of answers is always sent.
        num_answers = int(request.POST['numAnswers'])

        # The index of the correct answer.
        if 'correctAnswer' in request.POST:
            correct_answer = int(request.POST['correctAnswer'])
        else:
            correct_answer = 1

        # empty set
        answers = set()

        # For each answer returned
        
        print('num_answers: ' + str(num_answers))
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
                    answer.save();
                    answers.add(answer)

            # Note: in current version if the user selects a blank field as
            # the correct answer, errors may result.
            if x == correct_answer:

                # Load any existing records of which answer is correct and delete them
                existingCorrectAnswers = CorrectAnswers.objects.filter(questionID=question);
                for existingCorrectAnswer in existingCorrectAnswers:
                    existingCorrectAnswer.delete()

                # Create and save a new correct answer entry
                correctAnswerObject = CorrectAnswers();
                correctAnswerObject.questionID = question;
                correctAnswerObject.answerID = answer;
                correctAnswerObject.save();

        # Get the answers currently in the database
        existingAnswers = Answers.objects.filter(questionID=question)
        # Check them to make sure we didn't delete them this time around.
        for existingAnswer in existingAnswers:
            if existingAnswer not in answers:
                existingAnswer.delete()
        
        if 'challengeID' in request.POST:
            # save in ChallengesQuestions if not already saved            
  
            if  'questionId' in request.POST:                         
                challenge_question = ChallengesQuestions.objects.filter(challengeID=request.POST['challengeID']).filter(questionID=request.POST['questionId'])
                challenge_question.delete()

            challengeID = request.POST['challengeID']
            challenge = Challenges.objects.get(pk=int(challengeID))
            ChallengesQuestions.addQuestionToChallenge(question, challenge, int(request.POST['points']))

            #save question-skill pair to DB                    
            # first need to check whether a new skill is selected 
            
            if request.session['currentCourseID']:          
                courseID = Courses.objects.get(pk=int(request.session['currentCourseID']))
                
                # Processing and saving skills for the question in DB
                skillString = request.POST.get('all_Skills', "default")
                utils.saveQuestionSkills(skillString, question, challenge)
    
                skillIDselected = request.POST.get('Skill')
                if not skillIDselected == "":
                    questionSkill = QuestionsSkills()
                    questionSkill.skillID = Skills(skillIDselected)
                    questionSkill.questionID = Questions(question.questionID)
                    #questionSkill.courseID = courseID
                    questionSkill.challengeID = challenge
                    questionSkill.questionSkillPoints = int(request.POST['q_skill_points'])
                    questionSkill.save()

        # Processing and saving tags in DB                        #AA 3/24/15
        tagString = request.POST.get('tags', "default")
        utils.saveQuestionTags(tagString, question)
        
        redirectVar = redirect('/oneUp/instructors/challengeQuestionsList', context_dict)
        redirectVar['Location']+= '?challengeID='+request.POST['challengeID']
        return redirectVar
                
    #####################        
    # request.GET    
    else:
        num_answers = 4 #default number of blanks for new questions
        if request.GET:
            
            if Challenges.objects.filter(challengeID = request.GET['challengeID'],challengeName="Unassigned Problems"):
                context_dict["unassign"]= 1
                
            if 'challengeID' in request.GET:
                context_dict['challengeID'] = request.GET['challengeID']
                chall = Challenges.objects.get(pk=int(request.GET['challengeID']))
                context_dict['challengeName'] = chall.challengeName
                context_dict['challenge'] = True
            # In case we specify a different number of blanks
            if 'num_answers' in request.GET:
                num_answers = request.GET['num_answers']
                print('num_answers in GET  in IF: ' + str(num_answers))
            
            print('num_answers in GET: ' + str(num_answers))
                 
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
                    checked = "" #element must be completely omitted for not checked
                    for correctAnswer in correctAnswers:
                        if correctAnswer.answerID == answer:
                            checked = ' checked="true" '; 
                    ansChecked.append(checked)
                answersSet = True
                
                # Extract the tags from DB            
                context_dict['tags'] = utils.extractTags(question, "question")
                
                # Extract the skill                                        
                context_dict['all_Skills'] = utils.extractSkills(question, "question")
                
                if 'challengeID' in request.GET:
                    # get the challenge points for this problem to display
                    challenge_questions = ChallengesQuestions.objects.filter(challengeID=request.GET['challengeID']).filter(questionID=request.GET['questionId'])
                    context_dict['points'] = challenge_questions[0].points
                    
                    # set default skill points - 1                             # 03/17/2015 
                    context_dict['q_skill_points'] = int('1')
            
    if 'challengeID' in request.GET:
        print('challengeID  '+request.GET['challengeID'])  
                
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
    #else:
    return render(request,'Instructors/MultipleChoiceForm.html', context_dict)