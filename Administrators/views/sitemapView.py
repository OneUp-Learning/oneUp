
from django.template import RequestContext
from django.shortcuts import render

def sitemap(request):
 
    context_dict = { }
    
    context_dict["logged_in"]=request.user.is_authenticated
    if request.user.is_authenticated:
        context_dict["username"]=request.user.username
        
    return render(request,'sitemap.html', context_dict)