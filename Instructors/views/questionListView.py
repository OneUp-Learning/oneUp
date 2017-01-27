
from django.template import RequestContext
from django.shortcuts import render

from Instructors.models import StaticQuestions, Courses, Challenges, ChallengesQuestions

from django.contrib.auth.decorators import login_required

def makeContextDictForQuestionList():
    context_dict = { }

    q_ID = []      #PK for existing answers
    q_preview = []         
    q_type = []
    q_difficulty = []

#     if request.GET:
        
    questions = StaticQuestions.objects.all()
    for question in questions:
        q_ID.append(question.questionID)
        q_preview.append(question.preview)
        q_type.append(question.type)
        q_difficulty.append(question.difficulty)
            
        # The range part is the index numbers.
    context_dict['question_range'] = zip(range(1,questions.count()+1),q_ID,q_preview,q_type,q_difficulty)
    return context_dict

def makeContextDictForQuestionsInChallenge(challengeId, context_dict):    # 02/28/15
    #context_dict = { }
    
    questionObjects= []
    qlist = []
    q_ID = []      #PK for existing answers6
    q_preview = []         
    q_type = []
    q_difficulty = []

    # If questionId is specified then we load for editing.
    challenge = Challenges.objects.get(pk=int(challengeId))    
    context_dict['challenge'] = True
    context_dict['challengeID'] = challenge.challengeID
    context_dict['challengeName'] = challenge.challengeName
                      
    # Get the questions for this challenge 
    challenge_questions = ChallengesQuestions.objects.filter(challengeID=int(challengeId))
         
    for challenge_question in challenge_questions:
        questionObjects.append(challenge_question.questionID)
 
    for question in questionObjects:
        q_ID.append(question.questionID)
        q_preview.append(question.preview)
        q_type.append(question.type)
        q_difficulty.append(question.difficulty)        
        
    # The range part is the index numbers.
    #context_dict['question_range'] = zip(range(1,questionObjects.count+1),q_ID,q_preview,q_type)
    context_dict['question_range'] = zip(range(1,len(questionObjects)+1),q_ID,q_preview,q_type,q_difficulty)
    
    return context_dict

@login_required
def questionListView(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict = makeContextDictForQuestionList()
    
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
        
        # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        context_dict['course_Name'] = 'Not Selected'
    
    return render(request,'Instructors/QuestionsList.html', context_dict)
