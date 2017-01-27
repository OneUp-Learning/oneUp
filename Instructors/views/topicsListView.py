'''
Created on Oct 1, 2015

@author: Alex
'''
from django.template import RequestContext
from django.shortcuts import render
from Instructors.models import Skills, Courses, CoursesSkills, Topics, CoursesTopics
from django.contrib.auth.decorators import login_required

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
        #topic_Author = []         
        
        ctopics = CoursesTopics.objects.filter(courseID=currentCourse)
        for ct in ctopics:
            topic_ID.append(ct.topicID.topicID) 

            topics = Topics.objects.filter(topicID=ct.topicID.topicID)
            for tname in topics:
                topic_Name.append(tname.topicName)
                #topic_Author.append(tname.topicAuthor)
   
            # The range part is the index numbers.
        context_dict['topic_range'] = zip(range(1,ctopics.count()+1),topic_ID,topic_Name)

    return render(request,'Instructors/TopicsList.html', context_dict)
