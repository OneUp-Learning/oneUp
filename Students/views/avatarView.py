'''
Created on Nov 14, 2016

@author: Joel Evans
'''

from django.shortcuts import render, redirect
import glob, os

from django.contrib.auth.decorators import login_required
from Students.models import Courses, Student

def avatar(request):

	context_dict = {}
	
	extractPaths(context_dict)

	context_dict["logged_in"] = request.user.is_authenticated()
	if request.user.is_authenticated():
		context_dict["username"] = request.user.username
		
	# check if course was selected
	if 'currentCourseID' in request.session:
		currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
		context_dict['course_Name'] = currentCourse.courseName
	else:
		context_dict['course_Name'] = 'Not Selected'
		

	if request.POST: 
		avatarImage = request.POST['avatar'] # The Chosen Avatar Image Name
		print("badge image: "+str(avatarImage))
	
		student = Student.objects.get(user=request.user)
		student.avatarImage = avatarImage
		student.save()
		
		context_dict['avatar'] = avatarImage	
		return redirect('/oneUp/students/StudentCourseHome', context_dict)

	return render(request, 'Students/Avatar.html', context_dict)

def extractPaths(context_dict): #funcation used to get the names from the file locaiton
	avatarPath = []
	
	for name in glob.glob('static/images/avatars/*'):
		name = name.replace("\\","/")
		avatarPath.append(name)
		print(name)
	
	context_dict["avatarPaths"] = zip(range(1,len(avatarPath)+1), avatarPath)

