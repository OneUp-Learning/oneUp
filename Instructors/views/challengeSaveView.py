from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from Instructors.models import Challenges, Courses, Topics, CoursesTopics, ChallengesTopics
from Instructors.views import utils, challengeListView
from Instructors.views.utils import utcDate
from Instructors.constants import default_time_str

@login_required
def challengeSaveView(request):
    # Request the context of the request.
 
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
        context_dict['course_notselected'] = 'Please select a course'

    string_attributes = ['challengeName','challengeDifficulty', 'feedbackOption'];          ##'challengeCategory',

    #qdifficulties = ['easy', 'medium', 'hard']

    tagString = ""
    topic_ID = []
    topic_Name = []
    
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
        
        #get isGraded
        isVisible = str(request.POST.get('isVisible','false'))        
       
        # Copy all strings from POST to database object.
        for attr in string_attributes:
            setattr(challenge,attr,request.POST[attr])

        # get the logged in user for an author                            # 03/10/2015
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

        
        if(request.POST['startTime'] == ""):
            challenge.startTimestamp = utcDate(default_time_str, "%m/%d/%Y %I:%M:%S %p")
        else:
            challenge.startTimestamp = utcDate(request.POST['startTime'], "%m/%d/%Y %I:%M:%S %p")
        
        #if user does not specify an expiration date, it assigns a default value really far in the future
        #This assignment statement can be defaulted to the end of the course date if it ever gets implemented
        if(request.POST['endTime'] == ""):
            challenge.endTimestamp = utcDate(default_time_str, "%m/%d/%Y %I:%M:%S %p")
        else:
            challenge.endTimestamp = utcDate(request.POST['endTime'], "%m/%d/%Y %I:%M:%S %p")
        
        numberAttempts = int(request.POST.get("numberAttempts", 1))
        timeLimit = int(request.POST.get("timeLimit", 45))
        challenge.numberAttempts = numberAttempts
        challenge.timeLimit = timeLimit
                              
        # check if course was selected
        if 'currentCourseID' in request.session:                       
            currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
            challenge.courseID = currentCourse
            context_dict['course_Name'] = currentCourse.courseName
        else:
            context_dict['course_Name'] = 'Not Selected'
            challenge.courseID = ""
                       
        challenge.save();  #Save challenge to database
                    
        if str(request.POST.get('isGraded','false')) == 'false':
            # Processing and saving topics for the challenge in DB
            topicString = request.POST.get('all_Topics', "default")
            utils.saveChallengesTopics(topicString, challenge)

            topicIDselected = request.POST.get('Topic')
            if not topicIDselected == "":
                challengeTopic = ChallengesTopics()
                challengeTopic.topicID = Topics(topicIDselected)
                challengeTopic.challengeID = challenge
                challengeTopic.save()
                    
                        
        # Processing and saving tags in DB
        tagString = request.POST.get('tags', "default")
        utils.saveChallengeTags(tagString, challenge)
        
        
    if isGraded == "":
    	return redirect('/oneUp/instructors/challengesList?warmUp')
    else:
	    return redirect('/oneUp/instructors/challengesList')
    	
       


