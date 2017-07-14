'''
Created on Oct 1, 2015
Last updated on 07/12/2017

@author: Alex
'''
from django.shortcuts import render
from Instructors.models import Courses, Topics, CoursesTopics
from Instructors.constants import  unspecified_topic_name
from django.contrib.auth.decorators import login_required
from inspect import currentframe

@login_required
def topicsListView(request):
  
    context_dict = { }

    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
    
    # check if course was selected
    if not 'currentCourseID' in request.session:
        context_dict['course_Name'] = 'Not Selected'
        context_dict['course_notselected'] = 'Please select a course'
    else:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
          
        topic_ID = []      
        topic_Name = []
               
        ctopics = CoursesTopics.objects.filter(courseID=currentCourse)
        for ct in ctopics:
            topic_ID.append(ct.topicID.topicID) 

            topics = Topics.objects.filter(topicID=ct.topicID.topicID)
            for topic in topics:
                if not topic.topicName == unspecified_topic_name:   # do not display the unspecified topic
                    topic_Name.append(topic.topicName)

        context_dict['topic_range'] = zip(range(1,ctopics.count()+1),topic_ID,topic_Name)

    return render(request,'Instructors/TopicsList.html', context_dict)
