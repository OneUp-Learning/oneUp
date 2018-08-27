'''
Created on Nov 14, 2016

@author: Joel Evans
'''

from django.shortcuts import render, redirect
import glob

from Students.models import Student, StudentRegisteredCourses
from Students.views.utils import studentInitialContextDict
from django.contrib.auth.decorators import login_required
from django.template.context_processors import request

@login_required
def avatar(request):

	context_dict,currentCourse = studentInitialContextDict(request)


	if 'currentCourseID' in request.session:	
		sID = Student.objects.get(user=request.user)
		extractPaths(context_dict, currentCourse, sID)
	
	if request.POST: 
		avatarImage = request.POST['avatar'] # The Chosen Avatar Image Name
		print("avatar image: "+str(avatarImage))
	
		st_crs = StudentRegisteredCourses.objects.get(studentID=sID,courseID=currentCourse)	 
		st_crs.avatarImage = avatarImage
		st_crs.save()
		
		context_dict['avatar'] = avatarImage	
		return redirect('/oneUp/students/StudentCourseHome', context_dict)

	return render(request, 'Students/Avatar.html', context_dict)

def extractPaths(context_dict, currentCourse, sID): #function used to get the names from the file locaiton
	defaultAvatar = '/static/images/avatars/anonymous.png'
	
	#Find the users used avatar
	usedAvatars = ''
	st_crs = StudentRegisteredCourses.objects.get(studentID=sID,courseID=currentCourse)	 
	usedAvatars = st_crs.avatarImage
	print("#############  We are here ########### ")
	print("Used avatar: " + usedAvatars)
	
	#Get all the avatars
	avatarPath = []	
	absolutePath = []
	for name in glob.glob('static/images/avatars/*'):
		name = name.replace("\\","/")
		namec = '/'+name
		avatarPath.append(name)
		absolutePath.append(namec)
	
	#Check to make sure the students avatar still exisit if not chagne to default
	if not usedAvatars in absolutePath:
		st_crs.avatarImage = defaultAvatar
		st_crs.save()
		
	
	context_dict["avatarPaths"] = zip(range(1,len(avatarPath)+1), avatarPath)

