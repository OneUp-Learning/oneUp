'''
Created on Feb 05, 2015

@author: perryd
'''
from django.template import RequestContext
from django.shortcuts import redirect
from django.contrib.auth import logout

def LogoutView(request):
    logout(request)
    return redirect('/oneUp/home.html')