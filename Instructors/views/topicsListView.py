'''
Created on Oct 1, 2015

@author: Alex
'''
from django.template import RequestContext
from django.shortcuts import render
from Instructors.models import Skills, Courses, CoursesSkills, Topics, CoursesTopics,CoursesSubTopics
from django.contrib.auth.decorators import login_required
from inspect import currentframe
def get_linenumber():
    cf = currentframe()
    return cf.f_back.f_lineno

@login_required
def topicsListView(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
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
#        subTopicID = []
        
        
        ctopics = CoursesTopics.objects.filter(courseID=currentCourse)
        for ct in ctopics:
            topic_ID.append(ct.topicID.topicID) 

            topics = Topics.objects.filter(topicID=ct.topicID.topicID)
            for tname in topics:
                topic_Name.append(tname.topicName)

#             subTopics = CoursesSubTopics.objects.filter(topicID=ct.topicID.topicID)
#             for stid in subTopics:
#                 subTopicID.append(stid.subTopicID)
#             print(get_linenumber(),"subTopicID",subTopicID)
# #             The range part is the index numbers.
#         context_dict['topic_range'] = zip(range(1,ctopics.count()+1),topic_ID,topic_Name,subTopicID)
        context_dict['topic_range'] = zip(range(1,ctopics.count()+1),topic_ID,topic_Name)

    return render(request,'Instructors/TopicsList.html', context_dict)
