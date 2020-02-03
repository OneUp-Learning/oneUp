'''
Last updated on Sep 12, 2016

'''
from django.template import RequestContext
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

def loginView(request):
    context_dict = { }
    
    context_dict["logged_in"]=request.user.is_authenticated
    if request.user.is_authenticated:
        user = request.user
        context_dict["username"]=user.username
                
        if user.groups.filter(name='Teachers').exists():
            context_dict["is_teacher"] = True
        elif user.groups.filter(name='Admins').exists():
            context_dict["is_admin"] = True
        else:
            context_dict["is_student"] = True
    return render(request, 'home.html', context_dict)

@csrf_exempt
def login_interconnect(request):
  return loginView(request)
