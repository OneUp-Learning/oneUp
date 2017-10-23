from django.shortcuts import render, redirect
from Instructors.models import Answers, CorrectAnswers, Courses
from Instructors.models import Challenges, CoursesTopics, ChallengesTopics, StaticQuestions
from Instructors.models import ChallengesQuestions, MatchingAnswers
from Instructors.views import utils, challengeListView
from Instructors.views.utils import utcDate
from Instructors.constants import unspecified_topic_name, default_time_str
from django.contrib.auth.decorators import login_required

from time import time
from datetime import datetime


@login_required
def challengeCreateView(request):
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
                   
    questionObjects= []
    qlist = []
    topic_ID = []
    topic_Name = []
    
    context_dict['isVisible']=True
    context_dict['displayCorrectAnswer']= True
    
    string_attributes = ['challengeName', 'challengeDifficulty',               ##'isGraded','challengeCategory', 'challengeDifficulty'
                  'numberAttempts','timeLimit','challengePassword'
                  ];   
    
    # Fetch the topics for this course from the database.
    course_topics = CoursesTopics.objects.filter(courseID=currentCourse)   
    for ct in course_topics:
        topic_ID.append(ct.topicID.topicID)
        topic_Name.append(ct.topicID.topicName)
        
    unspecified_topic = CoursesTopics.objects.get(courseID=currentCourse, topicID__topicName=unspecified_topic_name).topicID
      
    
    # The range part is the index numbers.
    context_dict['topic_range'] = zip(range(1,course_topics.count()+1),topic_ID,topic_Name)
    
    if request.POST:

        # Check whether a new challenge or editing an existing challenge         
        if request.POST['challengeID']:
            challenge = Challenges.objects.get(pk=int(request.POST['challengeID']))
        else:
            # Create a NEW Challenge
            challenge = Challenges()
        
        #get isGraded
        isGraded = str(request.POST.get('isGraded','false'))  
        
        #get isVisible
        isVisible = str(request.POST.get('isVisible','false'))
        
        #get difficulty
        if(request.POST['challengeDifficulty']):
            challenge.challengeDifficulty = request.POST['challengeDifficulty']
        else:
            challenge.challengeDifficulty = ''
        context_dict['challengeDifficulty'] = challenge.challengeDifficulty
        
        displayCorrectAnswer = str(request.POST.get('displayCorrectAnswer','false'))  
        displayCorrectAnswerFeedback = str(request.POST.get('displayCorrectAnswerFeedback','false'))  
        #displayCorrectAnswerFeedback = str(request.POST.get('displayCorrectAnswerFeedback','false'))
        displayIncorrectAnswerFeedback = str(request.POST.get('displayIncorrectAnswerFeedback','false'))         
       
        # Copy all strings from POST to database object.
        for attr in string_attributes:
            if(attr in request.POST):
                setattr(challenge,attr,request.POST[attr])


        # get the logged in user for an author                           
        if request.user.is_authenticated():
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
            challenge.startTimestamp = utcDate(default_time_str, "%m/%d/%Y %I:%M:%S %p")
        else:
            challenge.startTimestamp = utcDate(request.POST['startTime'], "%m/%d/%Y %I:%M:%S %p")
        
        #if user does not specify an expiration date, it assigns a default value really far in the future
        #This assignment statement can be defaulted to the end of the course date if it ever gets implemented
        if(request.POST['endTime'] == ""):
            challenge.endTimestamp = utcDate(default_time_str, "%m/%d/%Y %I:%M:%S %p")
        else:
            if datetime.strptime(request.POST['endTime'], "%m/%d/%Y %I:%M:%S %p"):
                challenge.endTimestamp = utcDate(request.POST['endTime'], "%m/%d/%Y %I:%M:%S %p")
            else:
                challenge.endTimestamp = utcDate(default_time_str, "%m/%d/%Y %I:%M:%S %p")
        
        # Number of attempts
        if('unlimittedAttempts' in request.POST):
            challenge.numberAttempts = 99999   # unlimited attempts
        else:
            num = request.POST['numberAttempts']  #empty string and number 0 evaluate to false
            if not num:
                challenge.numberAttempts = 99999
            else:
                numberAttempts = int(request.POST.get("numberAttempts", 1))
                challenge.numberAttempts = numberAttempts

        # Time to complete the challenge
        if('unlimittedTime' in request.POST):
            challenge.timeLimit = 99999   # unlimited time
        else:
            time = request.POST['timeLimit']    #empty string and number 0 evaluate to false
            if not time:
                challenge.timeLimit = 99999
            else:
                timeLimit = int(request.POST.get("timeLimit", 45))
                challenge.timeLimit = timeLimit
        
#         challengePassword = request.POST.get("challengePassword")
#         challenge.challengePassword = challengePassword
        
#         if'feedbackOption' in request.POST:
#             challenge.feedbackOption = request.POST['feedbackOption']
#         else:
#             challenge.feedbackOption = 0
                              
        # check if course was selected
        if 'currentCourseID' in request.session:                        
            currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
            challenge.courseID = currentCourse
            context_dict['course_Name'] = currentCourse.courseName
        else:
            context_dict['course_Name'] = 'Not Selected'
            challenge.courseID = ""
                       
        challenge.save();  #Save challenge to database
        
        
        # Old Processing and saving topics for the challenge in DB and it's commented and the alternative one is used
        #topicsString = ''
        #topicsList = request.POST.getlist('topics[]')
         
        #for t in topicsList:
            #topicsString +=t+','
        #topicsString = 'relation,sql'
#         topicsString = request.POST.get('newTopics', "default")
#         if topicsString == "" and not request.POST['challengeID']:  # new challenge & no topic specified           
#             newChallTopicsObject = ChallengesTopics()
#             newChallTopicsObject.challengeID = challenge
#             newChallTopicsObject.topicID = unspecified_topic                
#             newChallTopicsObject.save()
#  
#         else:                       
#             utils.saveChallengesTopics(topicsString, challenge,unspecified_topic)                   
#        
        # Processing and saving topics for the challenge in DB
        utils.addTopicsToChallenge(challenge,request.POST.getlist('topics[]'),unspecified_topic)                 
        # Processing and saving tags in DB
        tagString = request.POST.get('tags', "default")
        utils.saveChallengeTags(tagString, challenge)
        
        if isGraded == "":
            return redirect('/oneUp/instructors/warmUpChallengeList')
        else:
            return redirect('/oneUp/instructors/challengesList')
    
    # GET        
    if request.GET:
        # In case we specify a different number of blanks
        if 'num_answers' in request.GET:
            num_answers = request.GET['num_answers']
            
        if 'warmUp' in request.GET:
            context_dict['warmUp']= 1
            
        # If questionId is specified then we load for editing.
        if 'challengeID' in request.GET:
            challenge = Challenges.objects.get(pk=int(request.GET['challengeID']))
            
            # Extract the tags from DB            
            context_dict['tags'] = utils.extractTags(challenge, "challenge")
                
            # Copy all of the attribute values into the context_dict to
            # display them on the page.
            challengeId= request.GET['challengeID']
            context_dict['challengeID']=request.GET['challengeID']
            
            context_dict['challengeDifficulty'] = challenge.challengeDifficulty  
            
            for attr in string_attributes:
                data = getattr(challenge,attr)
                if data == 99999:
                    context_dict[attr] = ""
                else:
                    context_dict[attr]= data
                          
            if challenge.numberAttempts == 99999:
                context_dict['unlimittedAttempts']=True
            else:
                context_dict['unlimittedAttempts']=False 
            
            if challenge.timeLimit == 99999:
                context_dict['unlimittedTime']=True
            else:
                context_dict['unlimittedTime']=False 
            
                          
            #if challenge.endTimestamp.strftime("%Y") < ("2900"): 
            etime = datetime.strptime(str(challenge.endTimestamp), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M:%S %p")
            print('etime ', etime)
            if etime != default_time_str: 
                print('etime2 ', etime)   
                context_dict['endTimestamp']=etime
            else:
                context_dict['endTimestamp']=""
            
            print(challenge.startTimestamp.strftime("%Y")) 
            if challenge.startTimestamp.strftime("%Y") < ("2900"):
                context_dict['startTimestamp']= datetime.strptime(str(getattr(challenge, 'startTimestamp')), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M %p")
            else:
                context_dict['startTimestamp']=""
            
            #context_dict['feedbackOption']= getattr(challenge,'feedbackOption')
    
            if challenge.isGraded:
                context_dict['isGraded']=True
            else:
                context_dict['isGraded']=False
                
            if challenge.isVisible:
                context_dict['isVisible']=True
            else:
                context_dict['isVisible']=False

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
            challenge_questions = ChallengesQuestions.objects.filter(challengeID=challengeId)
            
            for challenge_question in challenge_questions:
                #print("challenge_question.questionID: "+str(challenge_question.questionID))
                questionObjects.append(challenge_question.questionID)
            
            # Getting all the questions of the challenge except the matching question
            challengeDetails = Challenges.objects.filter(challengeID = challengeId)
            
            # If not challenge.isGraded:
            # Extract the topics                                       
            #context_dict['all_Topics'] = utils.extractTopics(challenge, "challenge")
            context_dict['all_Topics'] = utils.getTopicsForChallenge(challenge)
            # The following information is needed for the challenge 'view' option            
            for q in questionObjects:
                
                q_type = q.type
                if q_type in [1,2,3,4]:     # static problems
                    
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
                    
                    
                    #getting the matching questions of the challenge from database
                    matchlist = []
                    for match in MatchingAnswers.objects.filter(questionID=q.questionID):
                        matchdict = match.__dict__
                        matchdict['answers_count'] = range(1,int(len(answers))+1)
                        matchlist.append(matchdict)
                    questdict['matches']=matchlist
                    qlist.append(questdict)
                                   
                else:
                    
                    # TODO prepare information for displaying dynamic questions
                    qlist = []
    
            context_dict['question_range'] = zip(range(1,len(questionObjects)+1),qlist)

    
    if 'view' in request.GET:
        view = 1
    elif 'wView' in request.GET:
        context_dict['warmUp']= 1
        view = 1
    else:
        view = 0
        
    if view != 0:
        return render(request,'Instructors/ChallengeEditOutlook.html', context_dict)    #view
    else:   
        return render(request,'Instructors/ChallengeCreateForm.html', context_dict)     #edit
   

