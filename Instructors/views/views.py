from django.shortcuts import render

from django.template import RequestContext
from django.shortcuts import render

from django.http import HttpResponse

from django.forms.models import inlineformset_factory

from Instructors.forms import MultipleChoiceQuestionsForm, MultipleAnswerQuestionsForm
from Instructors.forms import MultipleChoiceQuestionsFormSet, MultipleAnswerQuestionsFormSet
from Instructors.models import StaticQuestions, Answers, CorrectAnswers

from django.contrib.auth.decorators import login_required

def index(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 

    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage is the same as {{ boldmessage }} in the template!
    context_dict = {'boldmessage': "I am bold font from the context"}

    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    return render(request,'Instructors/InstructorCourseHome.html', context_dict)  #DD

