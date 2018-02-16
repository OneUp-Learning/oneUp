from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from Instructors.models import Skills, Courses, CoursesSkills, Topics, CoursesTopics, CoursesSubTopics
from Instructors.constants import unspecified_topic_name, default_time_str
from Instructors.views.utils import utcDate
# from Instructors.views import utils, TopicsListView, subTopicsListView

from time import time
from datetime import datetime
from inspect import currentframe

def get_linenumber():
    cf = currentframe()
    return cf.f_back.f_lineno



@login_required
def subTopicsCreateView(request):
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
                   
    topicID = []
    topicName = []
    subTopicID = []
    subTopic_Name = []
#     displayDate = []

#     course_sub_topics = CoursesSubTopics.objects.filter(courseID=currentCourse)
         
#     for st in course_sub_topics:
#         subTopicID.append(st.subTopicID)
#         subTopic_Name.append(st.subTopicName)
#         topicID.append(st.topicID)

    # The range part is the index numbers.
#     print(get_linenumber(),'Print :: --> subTopic_Name',subTopic_Name)
#     
#     context_dict['sub_topic_range'] = zip(range(1,course_sub_topics.count()+1),subTopicID,subTopic_Name)
    string_attributes = ['topicName'];
    
    if request.POST:
        # Check whether a new subTopic or editing an existing subTopic
        print (get_linenumber(),"POST Request",request.POST['subTopicID'])
        if request.POST['subTopicID']:
            subtopic = CoursesSubTopics.objects.get(pk=int(request.POST['subTopicID']))
        else:
            print("POST MODE")
            # Create a NEW Challenge
            print (get_linenumber(),"POST Request",topicID)
            subtopic = CoursesSubTopics()
            subtopic.topicID  = Topics.objects.get(topicID=int(request.POST['topicID']))
            subtopic.courseID = Courses.objects.get(pk=int(request.session['currentCourseID']))
            
        subtopic.subTopicName = str(request.POST['subTopicName'])
        subtopic.subTopicPos = int(request.POST['subTopicPos'])
        subtopic.thresholdXP = int(request.POST['thresholdXP'])
        subtopic.thresholdSP = int(request.POST['thresholdSP'])

#         if(request.POST['displayDate'] == ""):
#             subtopic.displayDate = (datetime.datetime.strptime("12/31/2999 11:59:59 PM" ,"%m/%d/%Y %I:%M:%S %p"))
#         else:
        if datetime.strptime(request.POST['displayDate'], "%m/%d/%Y %I:%M %p"):
                subtopic.displayDate = utcDate(request.POST['displayDate'], "%m/%d/%Y %I:%M %p")
        else:
                subtopic.displayDate = utcDate(default_time_str,"%m/%d/%Y %I:%M:%S %p")
                              

        subtopic.save();  #Save subtopic to database
#         topics = Topics.objects.filter(topicID=subtopic.topicID.topicID)
#         for tname in topics:
#             context_dict['topicID']=tname.topicID
#         print (get_linenumber(),'context_dict',context_dict['topicID'])
        
        response = redirect('/oneUp/instructors/subTopicsListView', context_dict)
        response['Location'] +='?topicID=' + str(subtopic.topicID.topicID)
        return response
#         return redirect('/oneUp/instructors/subTopicsListView', context_dict)
#         return render(request,'/oneUp/instructors/subTopicsListView', context_dict) 
    
    # GET        
    if request.GET:

        print(get_linenumber(),"GET MODE")
        if 'topicID' in request.GET:
            topics = Topics.objects.filter(topicID=int(request.GET['topicID']))
            for tname in topics:
                topicName.append(tname.topicName)
                context_dict['topicID']=tname.topicID
                context_dict['topicName']=tname.topicName
        # If subTopicID is specified then we load for editing.
        if 'subTopicID' in request.GET:
            subtopic = CoursesSubTopics.objects.get(pk=int(request.GET['subTopicID']))
            
            print (get_linenumber(),"subtopic", subtopic)
                
            # Copy all of the attribute values into the context_dict to
            # display them on the page.
#             context_dict['topicID']=subtopic.topicID
            topics = Topics.objects.filter(topicID=subtopic.topicID.topicID)
            for tname in topics:
                topicName.append(tname.topicName)
                context_dict['topicID']=tname.topicID
                context_dict['topicName']=tname.topicName
            context_dict['subTopicID']=subtopic.subTopicID
            context_dict['subTopicName']=subtopic.subTopicName
            context_dict['currentCourse']=subtopic.courseID
            context_dict['subTopicPos']=subtopic.subTopicPos
            context_dict['thresholdXP']=subtopic.thresholdXP
            context_dict['thresholdSP']=subtopic.thresholdSP
            context_dict['displayDate']= getattr(subtopic, 'displayDate')

        return render(request,'Instructors/subTopicsCreate.html', context_dict)     #edit  

