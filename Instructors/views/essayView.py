#
# Last updated 03/24/2015
#

from django.template import RequestContext
from django.shortcuts import render
from django.shortcuts import redirect

from Instructors.models import Questions, StaticQuestions, Courses, CoursesSkills
from Instructors.models import Skills, QuestionsSkills, Challenges, ChallengesQuestions

from Instructors.views import utils
from Instructors.views.challengeListView import makeContextDictForQuestionsInChallenge
from Badges.enums import QuestionTypes

from django.contrib.auth.decorators import login_required

#EssayQuestionType = QuestionTypes.objects.get(pk=5)

@login_required
def essayForm(request):
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
    string_attributes = ['preview','questionText','difficulty','correctAnswerFeedback',
                  'incorrectAnswerFeedback','instructorNotes'];
        
    #raw string from the tags textbox
    tagString = request.POST.get('tags', "default")
     
    if 'view' in request.GET:
        context_dict['view'] = 1
        
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
        #question.type = EssayQuestionType
        question.type = QuestionTypes.essay;

        # get the author                            # 03/10/2015
        if request.user.is_authenticated():
            question.author = request.user.username
        else:
            question.author = ""

        question.save()  #Writes to database
        print(question)

        if 'challengeID' in request.POST:
            # save in ChallengesQuestions if not already saved        # 02/28/2015    
  
            if  'questionId' in request.POST:                         
                challenge_question = ChallengesQuestions.objects.filter(challengeID=request.POST['challengeID']).filter(questionID=request.POST['questionId'])
                challenge_question.delete()

            challengeID = request.POST['challengeID']
            challenge = Challenges.objects.get(pk=int(challengeID))
            ChallengesQuestions.addQuestionToChallenge(question, challenge, int(request.POST['points']))

            #save question-skill pair to db                   
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
                
    # request.GET                                   
    else:
        
        if request.GET:     
            if Challenges.objects.filter(challengeID = request.GET['challengeID'],challengeName="Unassigned Problems"):
                context_dict["unassign"]= 1
                
            if 'challengeID' in request.GET:
                context_dict['challengeID'] = request.GET['challengeID']
                chall = Challenges.objects.get(pk=int(request.GET['challengeID']))
                context_dict['challengeName'] = chall.challengeName
                context_dict['challenge'] = True

            # If questionId is specified then we load for editing.
            if 'questionId' in request.GET:
                question = StaticQuestions.objects.get(pk=int(request.GET['questionId']))
                
                # Copy all of the attribute values into the context_dict to
                # display them on the page.
                context_dict['questionId']=request.GET['questionId']
                for attr in string_attributes:
                    context_dict[attr]=getattr(question,attr)

                # Extract the tags from DB            
                context_dict['tags'] = utils.extractTags(question, "question")
                
                # Extract the skill                                        
                context_dict['all_Skills'] = utils.extractSkills(question, "question")
                
                if 'challengeID' in request.GET:
                    # get the points to display
                    challenge_questions = ChallengesQuestions.objects.filter(challengeID=request.GET['challengeID']).filter(questionID=request.GET['questionId'])
                    context_dict['points'] = challenge_questions[0].points
                    
                    # set default skill points - 1                             # 03/17/2015 
                    context_dict['q_skill_points'] = int('1')
            
#     if 'challengeID' in request.GET:
#         print('challengeID  '+request.GET['challengeID'])  
         
    # If we didn't run that code to load the values for the answers, then we make
    # blank lists.  We do this because we need to use a zipped list and a for
    # in order for the template stuff to be happy with us.  Doing that requires tha
    # all the lists have the same length

      
    if 'questionId' in request.POST:         
        #return redirect('challengeEditQuestionsView')
        return redirect('challengesView')

    return render(request,'Instructors/EssayForm.html', context_dict)
