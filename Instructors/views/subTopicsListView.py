'''
Created on Oct 1, 2015

@author: Alex
'''
from django.shortcuts import render
from Instructors.models import Topics,CoursesSubTopics
from Instructors.views.utils import initialContextDict
from django.contrib.auth.decorators import login_required
from inspect import currentframe

def get_linenumber():
    cf = currentframe()
    return cf.f_back.f_lineno

@login_required
def subTopicsListView(request):
    context_dict, currentCourse = initialContextDict(request)
      
    topic_ID = []      
    topic_Name = []
    subTopicID = []
    subTopicName =[]
    subTopicPos = []
    thresholdXP = []
    thresholdSP = []
    displayDate = []
    
    subTopics = CoursesSubTopics.objects.filter(topicID = request.GET['topicID'])
    for stid in subTopics:
                topic_ID.append(stid.topicID)
                subTopicID.append(stid.subTopicID)
                subTopicName.append(stid.subTopicName)
                subTopicPos.append(stid.subTopicPos)
                thresholdXP.append(stid.thresholdXP)
                thresholdSP.append(stid.thresholdSP)
                displayDate.append(stid.displayDate)
                print(get_linenumber(),"subTopicID",subTopicID)
                print(get_linenumber(),"subTopicName",subTopicName)
            
                topics = Topics.objects.filter(topicID=stid.topicID.topicID)
                for tname in topics:
                    topic_Name.append(tname.topicName)
    # The range part is the index numbers.
    context_dict['sub_topic_range'] = zip(range(1,subTopics.count()+1),topic_Name,subTopicPos,subTopicName,thresholdXP,thresholdSP,displayDate,subTopicID,topic_ID)

    return render(request,'Instructors/SubTopicsList.html', context_dict)
