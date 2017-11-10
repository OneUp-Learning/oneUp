from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Instructors.models import Topics, CoursesTopics
from Instructors.views import utils

@login_required
def topicsCreateView(request):
    
    context_dict,currentCourse = utils.initialContextDict(request)
    
    if request.POST:
        
        # There is an existing topic, edit it
        if request.POST['topicID']:
            topic = Topics.objects.get(pk=int(request.POST['topicID']))
            courseTopic = CoursesTopics.objects.get(topicID=topic, courseID=currentCourse)
            
        else:
            # Check if topic with this name already exists
            topics = Topics.objects.filter(topicName=request.POST['topicName'])
            if not topics:
                topic = Topics()
            else: 
                topic = topics[0]
                
            courseTopic = CoursesTopics()
            courseTopic.topicID = topic
            courseTopic.courseID = currentCourse
                
        topic.topicName = request.POST['topicName']                   
        topic.save()

        courseTopic.topicPos = int(request.POST['topicPos'])
        courseTopic.save()
                
    #################################
    #  get request
    else:
        if 'topicID' in request.GET:
            context_dict['topicID'] = request.GET['topicID']
            topic = Topics.objects.get(pk=int(request.GET['topicID']))
            context_dict['topicName']=topic.topicName
            ct = CoursesTopics.objects.get(topicID=topic,courseID=currentCourse)
            context_dict['topicPos']= str(ct.topicPos)
                   
    return render(request,'Instructors/TopicsCreate.html', context_dict)

