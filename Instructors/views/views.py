from django.shortcuts import render
from Instructors.views.utils import initialContextDict
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 

    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!
    # context_dict = {'boldmessage': "I am bold font from the context"}
    
    context_dict, currentCourse = initialContextDict(request)

    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    return render(request,'Instructors/InstructorCourseHome.html', context_dict)  #DD

