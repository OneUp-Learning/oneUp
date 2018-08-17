
from django.template import RequestContext
from django.shortcuts import render

def contactUsView(request):
 
    context_dict = { }
    
    context_dict["logged_in"]=request.user.is_authenticated
    if request.user.is_authenticated:
        context_dict["username"]=request.user.username
        
    return render(request,'contact-us.html', context_dict)