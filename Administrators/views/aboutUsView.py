
from django.template import RequestContext
from django.shortcuts import render

def aboutUsView(request):
 
    context_dict = { }
    
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
        
    return render(request,'aboutUs.html', context_dict)