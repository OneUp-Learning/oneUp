from django.template import RequestContext
from django.shortcuts import render, redirect
from Instructors.models import Answers, CorrectAnswers, Courses
from Instructors.models import Challenges,  Topics, CoursesTopics, ChallengesTopics, StaticQuestions
from Instructors.models import ChallengesQuestions, MatchingAnswers
from Instructors.views import utils, challengeListView
from django.contrib.auth.decorators import login_required
from Instructors.constants import unspecified_topic_name

from time import time
import datetime


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
    tagString = ""
    
    context_dict['isVisible']=True
    context_dict['feedbackOption1']= True
    
    string_attributes = ['challengeName',                ##'isGraded','challengeCategory', 'challengeDifficulty'
                  'numberAttempts','timeLimit','challengePassword'
                  ];   
    
    # Fetch the topics for this course from the database.
    course_topics = CoursesTopics.objects.filter(courseID=currentCourse)
         
    for t in course_topics:
        topic_ID.append(t.topicID.topicID)
        topic_Name.append(t.topicID.topicName)
    
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
        
        feedbackOption1 = str(request.POST.get('feedbackOption1','false'))  
        feedbackOption2 = str(request.POST.get('feedbackOption2','false'))  
        feedbackOption3 = str(request.POST.get('feedbackOption3','false'))        
       
        # Copy all strings from POST to database object.
        for attr in string_attributes:
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
        
        
        if feedbackOption1 == str("false"):
            feedbackOption1 =""
        challenge.feedbackOption1 = bool(feedbackOption1)
        context_dict = challengeListView.makeContextDictForChallengeList(context_dict, currentCourse, challenge.feedbackOption1)
        
        if feedbackOption2 == str("false"):
            feedbackOption2 =""
        challenge.feedbackOption2 = bool(feedbackOption2)
        context_dict = challengeListView.makeContextDictForChallengeList(context_dict, currentCourse, challenge.feedbackOption2)
        
        if feedbackOption3 == str("false"):
            feedbackOption3 =""
        challenge.feedbackOption3 = bool(feedbackOption3)
        context_dict = challengeListView.makeContextDictForChallengeList(context_dict, currentCourse, challenge.feedbackOption3)
        
        if(request.POST['startTime'] == ""):
            challenge.startTimestamp = (datetime.datetime.strptime("12/31/2999 11:59:59 PM" ,"%m/%d/%Y %I:%M:%S %p"))
        else:
            challenge.startTimestamp = datetime.datetime.strptime(request.POST['startTime'], "%m/%d/%Y %I:%M:%S %p")
        
        #if user does not specify an expiration date, it assigns a default value really far in the future
        #This assignment statement can be defaulted to the end of the course date if it ever gets implemented
        if(request.POST['endTime'] == ""):
            challenge.endTimestamp = (datetime.datetime.strptime("12/31/2999 11:59:59 PM" ,"%m/%d/%Y %I:%M:%S %p"))
        else:
            if datetime.datetime.strptime(request.POST['endTime'], "%m/%d/%Y %I:%M:%S %p"):
                challenge.endTimestamp = datetime.datetime.strptime(request.POST['endTime'], "%m/%d/%Y %I:%M:%S %p")
            else:
                challenge.endTimestamp = (datetime.datetime.strptime("12/31/2999 11:59:59 PM" ,"%m/%d/%Y %I:%M:%S %p"))
        
        # Number of attempts
        num = str(request.POST.get('unlimittedAttempts','false'))
        if num == str("true"):
            challenge.numberAttempts = 99999   # unlimited attempts
        else:
            num = request.POST['numberAttempts']  #empty string and number 0 evaluate to false
            if not num:
                challenge.numberAttempts = 99999
            else:
                numberAttempts = int(request.POST.get("numberAttempts", 1))
                challenge.numberAttempts = numberAttempts
        
        # Time to complete the challenge
        time = str(request.POST.get('unlimittedTime','false'))
        if time == str("true"):
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
        
        # Processing and saving topics for the challenge in DB
        topicsString = request.POST.get('all_Topics', "")
        topicSelected = request.POST.get('Topic')
        
        if topicsString == "":
            if topicSelected == "":
                topicsString = unspecified_topic_name
            else:
                topicsString = topicSelected  
        else:
            if not topicSelected == "":
                topicsString = topicsString + ',' +  topicSelected
                
        utils.saveChallengesTopics(topicsString, challenge)                   
                        
        # Processing and saving tags in DB
        tagString = request.POST.get('tags', "default")
        utils.saveChallengeTags(tagString, challenge)
        
        # Get information from DB to display on the Filter Questions web page  
        #challengeQuestionsFilter.challengeQuestionsFilter(challenge, context_dict)  # deleted this on 02/16/2016  - not clear what it does, perhaps remained from warm up challenges
        
        if isGraded == "":
            return redirect('/oneUp/instructors/challengesList?warmUp')
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
            
            context_dict['challengeDifficulty'] = getattr(challenge,'challengeDifficulty')  
            
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
            
                          
            if challenge.endTimestamp.strftime("%Y") < ("2900"):    
                context_dict['endTimestamp']=getattr(challenge, 'endTimestamp').strftime("%m/%d/%Y %I:%M:%S %p")
            else:
                context_dict['endTimestamp']=""
            
            print(challenge.startTimestamp.strftime("%Y")) 
            if challenge.startTimestamp.strftime("%Y") < ("2900"):
                context_dict['startTimestamp']=getattr(challenge, 'startTimestamp').strftime("%m/%d/%Y %I:%M:%S %p")
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

            if challenge.feedbackOption1:
                context_dict['feedbackOption1']=True
            else:
                context_dict['feedbackOption1']=False 
                
            if challenge.feedbackOption2:
                context_dict['feedbackOption2']=True
            else:
                context_dict['feedbackOption2']=False 
                
            if challenge.feedbackOption3:
                context_dict['feedbackOption3']=True
            else:
                context_dict['feedbackOption3']=False 
                           
            ##Get the challenge question information and put it in the context
            challenge_questions = ChallengesQuestions.objects.filter(challengeID=challengeId)
            
            for challenge_question in challenge_questions:
                #print("challenge_question.questionID: "+str(challenge_question.questionID))
                questionObjects.append(challenge_question.questionID)
            
            #getting all the questions of the challenge except the matching question
            challengeDetails = Challenges.objects.filter(challengeID = challengeId)
            
            #if not challenge.isGraded:
                # Extract the topics                                       
            context_dict['all_Topics'] = utils.extractTopics(challenge, "challenge")
            
                        
            for q in questionObjects:
                questdict = q.__dict__
                
                answers = Answers.objects.filter(questionID = q.questionID)
                answer_range = range(1,len(answers)+1)
                questdict['answers_with_count'] = zip(answer_range,answers)  
                questdict['match_with_count'] = zip(answer_range,answers) 
                
                staticQuestion = StaticQuestions.objects.get(pk=q.questionID)
                questdict['questionText']=staticQuestion.questionText

                questdict['typeID']=str(q.type)
                questdict['challengeID']= challengeId
                
                correct_answers = CorrectAnswers.objects.filter(questionID = q.questionID)
                print(correct_answers)
                canswer_range = range(1,len(correct_answers)+1)
                questdict['correct_answers'] = zip(canswer_range,correct_answers)
                
                
                #getting the matching questions of the challenge from database
                matchlist = []
                for match in MatchingAnswers.objects.filter(questionID=q.questionID):
                    matchdict = match.__dict__
                    matchdict['answers_count'] = range(1,int(len(answers))+1)
                    matchlist.append(matchdict)
                questdict['matches']=matchlist
                qlist.append(questdict)
                
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
 
    #return redirect('/oneUp/instructors/challengeEdit')
  

