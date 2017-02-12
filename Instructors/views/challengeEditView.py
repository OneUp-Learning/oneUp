# from django.template import RequestContext
# from django.shortcuts import render, redirect
# from Instructors.models import Answers, CorrectAnswers, Courses
# from Instructors.models import Challenges,  Topics, CoursesTopics, ChallengesTopics
# from Instructors.models import ChallengesQuestions, MatchingAnswers
# from Instructors.views import utils
# from django.contrib.auth.decorators import login_required
# from time import strftime
# import datetime
# 
# 
# @login_required
# def challengeEditView(request):
# 
#  
#     context_dict = { }
# 
#     context_dict["logged_in"]=request.user.is_authenticated()
#     if request.user.is_authenticated():
#         context_dict["username"]=request.user.username
# 
#     # check if course was selected
#     if 'currentCourseID' in request.session:
#         currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
#         context_dict['course_Name'] = currentCourse.courseName
#     else:
#         context_dict['course_Name'] = 'Not Selected'
#         
#             
#     questionObjects= []
#     qlist = []
#     topic_ID = []
#     topic_Name = []
#     
#     string_attributes = ['challengeName',                ##'isGraded','challengeCategory', 'challengeDifficulty'
#                   'numberAttempts','timeLimit', 'challengePassword'
#                   ];   
#     
#     # Fetch the topics for this course from the database.
#     course_topics = CoursesTopics.objects.filter(courseID=currentCourse)
#          
#     for t in course_topics:
#         topic_ID.append(t.topicID.topicID)
#         topic_Name.append(t.topicID.topicName)
#     
#     # The range part is the index numbers.
#     context_dict['topic_range'] = zip(range(1,course_topics.count()+1),topic_ID,topic_Name)
#     
#     if request.POST:
# 
#         # Check whether a new challenge or editing an existing challenge        
#         #if 'challengeID' in request.POST: 
#         if request.POST['challengeID']:
#             challenge = Challenges.objects.get(pk=int(request.POST['challengeID']))
#         else:
#             # Create a NEW Challenge
#             challenge = Challenges()
#         
#         #get isGraded
#         isGraded = str(request.POST.get('isGraded','false'))   
#         
#         #get isVisible
#         isVisible = str(request.POST.get('isVisible','false'))
#         
#         #get difficulty
#         if(request.POST['challengeDifficulty']):
#             challenge.challengeDifficulty = request.POST['challengeDifficulty']
#         else:
#             challenge.challengeDifficulty = ''
#         context_dict['challengeDifficulty'] = challenge.challengeDifficulty
#         
#         feedbackOption1 = str(request.POST.get('feedbackOption1','false'))  
#         feedbackOption2 = str(request.POST.get('feedbackOption2','false'))  
#         feedbackOption3 = str(request.POST.get('feedbackOption3','false'))      
# 
#         # Copy all strings from POST to database object.
#         for attr in string_attributes:
#             setattr(challenge,attr,request.POST[attr])
#         
#         # only empty strings return false when converted to boolean    
#         if isGraded == str("false"):
#             isGraded =""
#         challenge.isGraded = bool(isGraded)
# 
#          # only empty strings return false when converted to boolean    
#         if isVisible == str("false"):
#             isVisible =""
#         challenge.isVisible = bool(isVisible)
#         context_dict = challengeListView.makeContextDictForChallengeList(context_dict, currentCourse, challenge.isVisible)
#         
#         
#         if feedbackOption1 == str("false"):
#             feedbackOption1 =""
#         challenge.feedbackOption1 = bool(feedbackOption1)
#         context_dict = challengeListView.makeContextDictForChallengeList(context_dict, currentCourse, challenge.feedbackOption1)
#         
#         if feedbackOption2 == str("false"):
#             feedbackOption2 =""
#         challenge.feedbackOption2 = bool(feedbackOption2)
#         context_dict = challengeListView.makeContextDictForChallengeList(context_dict, currentCourse, challenge.feedbackOption2)
#         
#         if feedbackOption3 == str("false"):
#             feedbackOption3 =""
#         challenge.feedbackOption3 = bool(feedbackOption3)
#         context_dict = challengeListView.makeContextDictForChallengeList(context_dict, currentCourse, challenge.feedbackOption3)
#         
#         if(request.POST['startTime'] == ""):
#             challenge.startTimestamp = (datetime.datetime.strptime("12/31/2999 11:59:59 PM" ,"%m/%d/%Y %I:%M:%S %p"))
#         else:
#             challenge.startTimestamp = datetime.datetime.strptime(request.POST['startTime'], "%m/%d/%Y %I:%M:%S %p")
#         
#         #if user does not specify an expiration date, it assigns a default value really far in the future
#         #This assignment statement can be defaulted to the end of the course date if it ever gets implemented
#         if(request.POST['endTime'] == ""):
#             challenge.endTimestamp = (datetime.datetime.strptime("12/31/2999 11:59:59 PM" ,"%m/%d/%Y %I:%M:%S %p"))
#         else:
#             challenge.endTimestamp = datetime.datetime.strptime(request.POST['endTime'], "%m/%d/%Y %I:%M:%S %p")
#         
#         num = request.POST['numberAttempts']  #empty string and number 0 evaluate to false
#         if not num:
#             challenge.numberAttempts = 999999
#         else:
#             numberAttempts = int(request.POST.get("numberAttempts", 1))
#             challenge.numberAttempts = numberAttempts
#         
#         num = request.POST['timeLimit']    
#         if not num:
#             challenge.timeLimit = 999999
#         else:
#             timeLimit = int(request.POST.get("timeLimit", 45))
#             challenge.timeLimit = timeLimit
#             
#         challenge.challengeAuthor = request.user.username
#         challenge.startTimestamp = strftime("%Y-%m-%d %H:%M:%S")
#         #if user does not specify an expiration date, it assigns a default value really far in the future
#         #This assignment statement can be defaulted to the end of the course date if it ever gets implemented
#         if(request.POST['endTime'] == ""):
#             challenge.endTimestamp = (datetime.datetime.strptime("12/31/2999 11:59:59 PM" ,"%m/%d/%Y %I:%M:%S %p"))
#         else:
#             challenge.endTimestamp = datetime.datetime.strptime(request.POST['endTime'], "%m/%d/%Y %I:%M:%S %p")
#                        
#         challenge.save();  #Save challenge to database
#         
#         # save Challenges Topics pair to db        
#         # first need to check whether a new topic is selected 
#         if request.session['currentCourseID']:          # we presume the course is selected!!!!!!!!!!!!!!!!!!!!!!!!!
#             courseID = Courses.objects.get(pk=int(request.session['currentCourseID']))
#             
#             if str(request.POST.get('isGraded','false')) == 'false':
#                 # Processing and saving topics for the challenge in DB
#                 topicString = request.POST.get('all_Topics', "default")
#                 utils.saveChallengesTopics(topicString, challenge)
# 
#                 topicIDselected = request.POST.get('Topic')
#                 if not topicIDselected == "":
#                     challengeTopic = ChallengesTopics()
#                     challengeTopic.topicID = Topics(topicIDselected)
#                     challengeTopic.challengeID = challenge
#                     challengeTopic.save()
#             else:   
#                 utils.saveChallengesTopics('',challenge)
#         # Processing and saving tags in DB
#         tagString = request.POST.get('tags', "default")
#         #utils.saveTags(tagString, challenge, "challenge")
#         utils.saveChallengeTags(tagString, challenge)    
#     
#         if "done" in request.POST: 
#             if isGraded == "":
#                 print('not graded')
#                 return redirect('/oneUp/instructors/challengesWarmUpList')
#             else:
#                 print('graded')
#                 return redirect('/oneUp/instructors/challengesList')
#         
#             #return redirect('/oneUp/instructors/challengesList')
#         else:
#             challengeId = challenge.challengeID
#             challenge_exists = True
#     
#     if request.GET:
#         # If questionId is specified then we load for editing.
#         if request.GET['challengeID']:
#             challenge = Challenges.objects.get(pk=int(request.GET['challengeID']))
#             
#             # Extract the tags from DB            
#             context_dict['tags'] = utils.extractTags(challenge, "challenge")
#                 
#             # Copy all of the attribute values into the context_dict to
#             # display them on the page.
#             challengeId= request.GET['challengeID']
#             challenge_exists = True
#             
#             context_dict['endTimestamp']=getattr(challenge, 'endTimestamp').strftime("%m/%d/%Y %I:%M:%S %p")
#             
#         else:
#             challenge_exists = False
# 
#     if challenge_exists:
#         context_dict['challengeID']=challengeId
#         
#         context_dict['challengeDifficulty'] = challenge.challengeDifficulty
#         
#         for attr in string_attributes:
#             data = getattr(challenge,attr)
#             if data == 999999:
#                 context_dict[attr] = ""
#             else:
#                 context_dict[attr]= data
#     
#         if challenge.isGraded:
#             context_dict['isGraded']=True
#         else:
#             context_dict['isGraded']=False
#                     
#         ##Get the challenge question infor. and put it int he context
#         challenge_questions = ChallengesQuestions.objects.filter(challengeID=challengeId)
#         
#         for challenge_question in challenge_questions:
#             questionObjects.append(challenge_question.questionID)
#         
#         #getting all the questions of the challenge except the matching question
#         challengeDetails = Challenges.objects.filter(challengeID = challengeId)
#         
#         if not challenge.isGraded:
#             # Extract the topics                                       
#             context_dict['all_Topics'] = utils.extractTopics(challenge, "challenge")
#                 
#         for q in questionObjects:
#             questdict = q.__dict__
#             
#             answers = Answers.objects.filter(questionID = q.questionID)
#             answer_range = range(1,len(answers)+1)
#             questdict['answers_with_count'] = zip(answer_range,answers)  
#             questdict['match_with_count'] = zip(answer_range,answers) 
#             
#             
#             questdict['typeID']=str(q.type)
#             questdict['challengeID']= challengeId
#             
#             correct_answers = CorrectAnswers.objects.filter(questionID = q.questionID)
#             canswer_range = range(1,len(correct_answers)+1)
#             questdict['correct_answers'] = zip(canswer_range,correct_answers)
#             
#             
#             #getting the matching questions of the challenge from database
#             matchlist = []
#             for match in MatchingAnswers.objects.filter(questionID=q.questionID):
#                 matchdict = match.__dict__
#                 matchdict['answers_count'] = range(1,int(len(answers))+1)
#                 matchlist.append(matchdict)
#             questdict['matches']=matchlist
#             qlist.append(questdict)
#             
#         context_dict['question_range'] = zip(range(1,len(questionObjects)+1),qlist)
#     
#     
#     if 'view' in request.GET:
#         view = 1
#     elif 'wView' in request.GET:
#         context_dict['warmUp']= 1
#         view = 1
#     else:
#         view = 0
#         
#     if view != 0: 
#         return render(request,'Instructors/ChallengeEditOutlook.html', context_dict)
#     else:     
#         return render(request,'Instructors/ChallengeEdit.html', context_dict)
# 
#   

