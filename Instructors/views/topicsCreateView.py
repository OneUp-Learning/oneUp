from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from Instructors.models import Topics, CoursesTopics
from Instructors.views import utils
from oneUp.decorators import instructorsCheck

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def topicsCreateView(request):
    
    context_dict,currentCourse = utils.initialContextDict(request)
    
    if request.POST:
        
        # Check if topic with this name already exists
        topics = Topics.objects.filter(topicName=request.POST['topicName'])
        if topics:
            topic = topics[0]
        else: 
            topic = Topics()           
            topic.topicName = request.POST['topicName']                   
            topic.save()
            

        courseTopics = CoursesTopics.objects.filter(topicID=topic, courseID=currentCourse)
        if courseTopics:  
            courseTopic = courseTopics[0]                    
        else:
            courseTopic = CoursesTopics()
            courseTopic.topicID = topic
            courseTopic.courseID = currentCourse
                
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

