from django.shortcuts import render, redirect
from Instructors.models import Answers, CorrectAnswers
from Instructors.models import Challenges, CoursesTopics, StaticQuestions
from Instructors.models import ChallengesQuestions, MatchingAnswers
from Instructors.views import challengeListView
from Instructors.views.utils import localizedDate, utcDate, initialContextDict, autoCompleteTopicsToJson, addTopicsToChallenge, saveTags, getTopicsForChallenge, extractTags
from Instructors.constants import unspecified_topic_name, default_time_str
from django.contrib.auth.decorators import login_required, user_passes_test
from decimal import Decimal

from Badges.enums import ObjectTypes

from time import time
from datetime import datetime

from oneUp.logger import logger

from oneUp.decorators import instructorsCheck     

import re

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')   
def challengeCreateView(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
    context_dict, currentCourse = initialContextDict(request)
                   
    questionObjects= []
    qlist = []
    topic_ID = []
    topic_Name = []
    

    context_dict['isVisible']=True
    context_dict['displayCorrectAnswer']= True
    
    string_attributes = ['challengeName', 'challengeDifficulty',               ##'isGraded','challengeCategory', 'challengeDifficulty'
                  'numberAttempts','timeLimit','challengePassword','manuallyGradedScore'
                  ];   
    
    # Fetch the topics for this course from the database.
    course_topics = CoursesTopics.objects.filter(courseID=currentCourse)   
    for ct in course_topics:
        topic_ID.append(ct.topicID.topicID)
        topic_Name.append(ct.topicID.topicName)
        
    unspecified_topic = CoursesTopics.objects.get(courseID=currentCourse, topicID__topicName=unspecified_topic_name).topicID
      
    context_dict['topicsAuto'], context_dict['createdTopics'] = autoCompleteTopicsToJson(currentCourse)
    
    if request.method == "POST":
        logger.debug("[POST] " + str(context_dict))
        # Check whether a new challenge or editing an existing challenge         
        if request.POST['challengeID']:
            challenge = Challenges.objects.get(pk=int(request.POST['challengeID']))
        else:
            # Create a NEW Challenge
            challenge = Challenges()
            challenge.courseID = currentCourse
        
        #get isGraded
        isGraded = str(request.POST.get('isGraded','false'))
        print("isGraded post")
        print(isGraded)  
        
        #get isVisible
        isVisible = str(request.POST.get('isVisible','false'))
        
        #get randomization GGM
        isRandomized = str(request.POST.get('randomizeProblems','false'))
        
        #get difficulty
        if('challengeDifficulty' in request.POST):
            challenge.challengeDifficulty = request.POST['challengeDifficulty']
        else:
            challenge.challengeDifficulty = ''
        context_dict['challengeDifficulty'] = challenge.challengeDifficulty
        
        displayCorrectAnswer = str(request.POST.get('displayCorrectAnswer','false'))  
        displayCorrectAnswerFeedback = str(request.POST.get('displayCorrectAnswerFeedback','false'))  
        displayIncorrectAnswerFeedback = str(request.POST.get('displayIncorrectAnswerFeedback','false'))    
        try:     
            challenge.curve = Decimal(request.POST.get("curve", 0))
        except:
            challenge.curve = Decimal(0)

        # Copy all strings from POST to database object.
        for attr in string_attributes:
            if(attr in request.POST):
                setattr(challenge,attr,request.POST[attr])
        
        try:     
            challenge.manuallyGradedScore = Decimal(request.POST.get("manuallyGradedScore", 0))
        except:
            challenge.manuallyGradedScore = Decimal(0)

        # get the logged in user for an author                           
        if request.user.is_authenticated:
            challenge.challengeAuthor = request.user.username
        else:
            challenge.challengeAuthor = ""        
         
        # only empty strings return false when converted to boolean    
        if isGraded == str("false"):
            isGraded =""
        challenge.isGraded = bool(isGraded)
        context_dict = challengeListView.makeContextDictForChallengeList(context_dict, currentCourse, challenge.isGraded)

        # only empty strings return false when converted to boolean
        if isVisible == str("false"):
            isVisible =""
        challenge.isVisible = bool(isVisible)
        context_dict = challengeListView.makeContextDictForChallengeList(context_dict, currentCourse, challenge.isVisible)
        
        # only empty strings return false when converted to boolean
        if isRandomized == str("false"):
            isRandomized =""
        challenge.isRandomized = bool(isRandomized)
        context_dict = challengeListView.makeContextDictForChallengeList(context_dict, currentCourse, challenge.isRandomized)
        
        if displayCorrectAnswer == str("false"):
            displayCorrectAnswer =""
        challenge.displayCorrectAnswer = bool(displayCorrectAnswer)
        context_dict = challengeListView.makeContextDictForChallengeList(context_dict, currentCourse, challenge.displayCorrectAnswer)
        
        if displayCorrectAnswerFeedback == str("false"):
            displayCorrectAnswerFeedback =""
        challenge.displayCorrectAnswerFeedback = bool(displayCorrectAnswerFeedback)
        context_dict = challengeListView.makeContextDictForChallengeList(context_dict, currentCourse, challenge.displayCorrectAnswerFeedback)
        
        if displayIncorrectAnswerFeedback == str("false"):
            displayIncorrectAnswerFeedback =""
        challenge.displayIncorrectAnswerFeedback = bool(displayIncorrectAnswerFeedback)
        context_dict = challengeListView.makeContextDictForChallengeList(context_dict, currentCourse, challenge.displayIncorrectAnswerFeedback)
        
        
        if(request.POST['startTime'] == ""):
            challenge.startTimestamp = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
        else:
            challenge.startTimestamp = localizedDate(request, request.POST['startTime'], "%m/%d/%Y %I:%M %p")
        
        #if user does not specify an expiration date, it assigns a default value really far in the future
        #This assignment statement can be defaulted to the end of the course date if it ever gets implemented
        if(request.POST['endTime'] == ""):
            challenge.endTimestamp = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
        else:
            if datetime.strptime(request.POST['endTime'], "%m/%d/%Y %I:%M %p"):
                challenge.endTimestamp = localizedDate(request, request.POST['endTime'], "%m/%d/%Y %I:%M %p")                
            else:
                challenge.endTimestamp = utcDate(default_time_str, "%m/%d/%Y %I:%M %p")
        
        # Number of attempts
        if('unlimitedAttempts' in request.POST):
            challenge.numberAttempts = 99999   # unlimited attempts
        else:
            num = request.POST['numberAttempts']  #empty string and number 0 evaluate to false
            if not num:
                challenge.numberAttempts = 99999
            else:
                numberAttempts = int(request.POST.get("numberAttempts", 1))
                challenge.numberAttempts = numberAttempts

        # Time to complete the challenge
        if('unlimitedTime' in request.POST):
            challenge.timeLimit = 99999   # unlimited time
        else:
            time = request.POST['timeLimit']    #empty string and number 0 evaluate to false
            if not time:
                challenge.timeLimit = 99999
            else:
                timeLimit = int(request.POST.get("timeLimit", 45))
                challenge.timeLimit = timeLimit
        print("challenge")
        print(challenge)                      
        challenge.save()  #Save challenge to database
        # check if course was selected
        addTopicsToChallenge(challenge,request.POST['topics'],unspecified_topic, currentCourse)                 
        # Processing and saving tags in DB
        saveTags(request.POST['tags'], challenge, ObjectTypes.challenge)
        

        
        if isGraded == "":
            return redirect('/oneUp/instructors/warmUpChallengeList')
        else:
            return redirect('/oneUp/instructors/challengesList')
    
    elif request.method == "GET":
        # In case we specify a different number of blanks
        if 'num_answers' in request.GET:
            num_answers = request.GET['num_answers']
            
        if 'warmUp' in request.GET:
            context_dict['warmUp']= 1
           
        # If challengeID is specified then we load for editing.
        if 'challengeID' in request.GET:
            challenge = Challenges.objects.get(pk=int(request.GET['challengeID']))
                
            # Copy all of the attribute values into the context_dict to
            # display them on the page.
            challengeId= request.GET['challengeID']
            context_dict['challengeID']=request.GET['challengeID']
            
            context_dict['challengeDifficulty'] = challenge.challengeDifficulty  
            context_dict['curve'] = challenge.curve
            
            for attr in string_attributes:
                data = getattr(challenge,attr)
                if data == 99999:
                    context_dict[attr] = ""
                else:
                    context_dict[attr]= data
                          
            if challenge.numberAttempts == 99999:
                context_dict['unlimitedAttempts']=True
            else:
                context_dict['unlimitedAttempts']=False 
            
            if challenge.timeLimit == 99999:
                context_dict['unlimitedTime']=True
            else:
                context_dict['unlimitedTime']=False 
            

            startTime = challenge.startTimestamp.strftime("%m/%d/%Y %I:%M %p")
            if startTime != default_time_str:
                context_dict['startTimestamp']= startTime
            else:
                context_dict['startTimestamp']= ""

            endTime = challenge.endTimestamp.strftime("%m/%d/%Y %I:%M %p")
            if endTime != default_time_str: 
                context_dict['endTimestamp']= endTime
            else:
                context_dict['endTimestamp']= ""

    
            if challenge.isGraded:
                context_dict['isGraded']=True
            else:
                context_dict['isGraded']=False
                
            if challenge.isVisible:
                context_dict['isVisible']=True
            else:
                context_dict['isVisible']=False
                
            if challenge.isRandomized:
                context_dict['randomizeProblems']=True
            else:
                context_dict['randomizeProblems']=False

            if challenge.displayCorrectAnswer:
                context_dict['displayCorrectAnswer']=True
            else:
                context_dict['displayCorrectAnswer']=False 
                
            if challenge.displayCorrectAnswerFeedback:
                context_dict['displayCorrectAnswerFeedback']=True
            else:
                context_dict['displayCorrectAnswerFeedback']=False 
             
            if challenge.displayIncorrectAnswerFeedback:
                context_dict['displayIncorrectAnswerFeedback']=True
            else:
                context_dict['displayIncorrectAnswerFeedback']=False 
                 
                           
            # Get the challenge question information and put it in the context
            challenge_questions = ChallengesQuestions.objects.filter(challengeID=challengeId).order_by('questionPosition')
            
            for challenge_question in challenge_questions:
                questionObjects.append(challenge_question.questionID)
            
            # Getting all the questions of the challenge except the matching question
            challengeDetails = Challenges.objects.filter(challengeID = challengeId)
            
            # Extract the topics                                       
            context_dict['topics'] = getTopicsForChallenge(challenge)
            # Extract the tags from DB            
            context_dict['tags'] = extractTags(challenge, "challenge")

            #context_dict['all_Topics'] = utils.extractTopics(challenge, "challenge")
#             allTopics = utils.getTopicsForChallenge(challenge)
#             topicNames = ""
#             
#             for t in allTopics:
#                 topicNames += t['name'] +"\t\t"
#                 
#             context_dict['topics_str'] = topicNames
#             context_dict['all_Topics'] = utils.getTopicsForChallenge(challenge)

            # The following information is needed for the challenge 'view' option            
            for q in questionObjects:
                
                q_type = q.type
                # 8 is parsons
                if q_type in [1,2,3,4,8]:     # static problems
                    
                    questdict = q.__dict__
                    
                    answers = Answers.objects.filter(questionID = q.questionID)
                    answer_range = range(1,len(answers)+1)
                    questdict['answers_with_count'] = list(zip(answer_range,answers))
                    questdict['match_with_count'] = zip(answer_range,answers) 
                    
                    staticQuestion = StaticQuestions.objects.get(pk=q.questionID)
                    questdict['questionText']=staticQuestion.questionText
    
                    questdict['typeID']=str(q.type)
                    questdict['challengeID']= challengeId
                    
                    correct_answers = CorrectAnswers.objects.filter(questionID = q.questionID)
                    print(correct_answers)
                    canswer_range = range(1,len(correct_answers)+1)
                    questdict['correct_answers'] = list(zip(canswer_range,correct_answers))
                    
                    question_point = ChallengesQuestions.objects.get(challengeID=challengeId, questionID=q)
                    questdict['point'] = question_point.points
                    
                    #getting the matching questions of the challenge from database
                    matchlist = []
                    for match in MatchingAnswers.objects.filter(questionID=q.questionID):
                        matchdict = match.__dict__
                        matchdict['answers_count'] = range(1,int(len(answers))+1)
                        matchlist.append(matchdict)
                    questdict['matches']=matchlist
                    qlist.append(questdict)
                    
                    if q_type == 8:
                        answers = Answers.objects.filter(questionID=q.questionID)
                        if answers:
                            answer = answers[0]
                            print("Answer", repr(answer))
                            answer = repr(answer)
                            
                            #regex the answer, swap out the numbers, add a newline after lang and indent\n
                            answer = re.sub("^<Answers: \d{3},", "# ", answer)
                            answer = re.sub("ue;", "ue;\n", answer)
                            answer = re.sub("se;", "se;\n", answer)
                            questdict['modelSolution'] = answer 
                              
                else:
                    # TODO prepare information for displaying dynamic questions
                    qlist = []
        else:
            context_dict['topics'] = []
            context_dict['tags'] = []
            context_dict['isVisible']= True
            context_dict['displayCorrectAnswer']= True        
            context_dict['manuallyGradedScore'] = '0'    
            context_dict['curve'] = '0' 

        context_dict['question_range'] = zip(range(1,len(questionObjects)+1),qlist)
        logger.debug("[GET] " + str(context_dict))
        
    if 'wView' in request.GET:
        context_dict['warmUp']= 1
        view = 1
    elif 'view' in request.GET:
        view = 1
    else:
        view = 0
    context_dict['view'] = view == 1
    return render(request,'Instructors/ChallengeCreateForm.html', context_dict)     #edit
   

