'''
Created on Oct 1, 2015
Last updated on 07/12/2017

@author: Alex
'''
from django.shortcuts import render
from Instructors.models import Topics, CoursesTopics
from Instructors.constants import  unspecified_topic_name
from Instructors.views import utils
from django.contrib.auth.decorators import login_required


@login_required
def topicsListView(request):
  
    context_dict,currentCourse = utils.initialContextDict(request)   
           
    topicID = []      
    topicName = []
    topicPos = []
           
    ctopics = CoursesTopics.objects.filter(courseID=currentCourse)
    for ct in ctopics:
        tId = ct.topicID.topicID
        print(ct)
         
        topic = Topics.objects.get(topicID=tId)
        print(topic)
        if not topic.topicName == unspecified_topic_name:   # do not display the unspecified topic
            topicID.append(tId)
            topicName.append(topic.topicName)
            topicPos.append(str(ct.topicPos))

    context_dict['topic_range'] = sorted(list(zip(range(1,ctopics.count()+1),topicID,topicName,topicPos)),key=lambda tup: tup[3])

    return render(request,'Instructors/TopicsList.html', context_dict)
