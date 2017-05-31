from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Instructors.models import Courses, Topics, CoursesTopics

@login_required
def topicsCreateView(request):

 
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

    string_attributes = ['topicName'];
    
    if request.POST:
        
        # There is an existing topic, edit it
        if request.POST['topicID']:
            topic = Topics.objects.get(pk=int(request.POST['topicID']))
        else:
            # Check if topic with this name already exists
            topics = Topics.objects.filter(topicName=request.POST['topicName'])
            if not topics:
                topic = Topics()
                topic.topicName = request.POST['topicName']                   
                topic.save()
        
                courseTopic = CoursesTopics()
                courseTopic.courseID = Courses.objects.get(pk=int(request.session['currentCourseID']))
                courseTopic.topicID = topic
                courseTopic.save()
                
    #################################
    #  get request
    else:
        if 'topicID' in request.GET:
            context_dict['topicID'] = request.GET['topicID']
            topic = Topics.objects.get(pk=int(request.GET['topicID']))
            for attr in string_attributes:
                context_dict[attr]=getattr(topic,attr)
       
    return render(request,'Instructors/TopicsCreate.html', context_dict)

