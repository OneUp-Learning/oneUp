'''
Created on Nov 14, 2016

@author: Joel Evans
'''

from django.shortcuts import render, redirect
import glob

from Students.models import Student, StudentRegisteredCourses
from Students.views.utils import studentInitialContextDict

def avatar(request):

	context_dict,currentCourse = studentInitialContextDict(request)

# 	context_dict = {}
# 
# 	context_dict["logged_in"] = request.user.is_authenticated()
# 	if request.user.is_authenticated():
# 		context_dict["username"] = request.user.username
# 		sID = Student.objects.get(user=request.user)		
# 		
# 	# check if course was selected
# 	if 'currentCourseID' in request.session:
# 		currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
# 		context_dict['course_Name'] = currentCourse.courseName
# 		st_crs = StudentRegisteredCourses.objects.get(studentID=sID,courseID=currentCourse)	  		
# 		context_dict['avatar'] = st_crs.avatarImage
# 	else:
# 		context_dict['course_Name'] = 'Not Selected'

	if 'currentCourseID' in request.session:	
		extractPaths(context_dict, currentCourse)
		sID = Student.objects.get(user=request.user)
	
	if request.POST: 
		avatarImage = request.POST['avatar'] # The Chosen Avatar Image Name
		print("avatar image: "+str(avatarImage))
	
		st_crs = StudentRegisteredCourses.objects.get(studentID=sID,courseID=currentCourse)	 
		st_crs.avatarImage = avatarImage
		st_crs.save()
		
		context_dict['avatar'] = avatarImage	
		return redirect('/oneUp/students/StudentCourseHome', context_dict)

	return render(request, 'Students/Avatar.html', context_dict)

def extractPaths(context_dict, currentCourse): #funcation used to get the names from the file locaiton

	#Find all used avatars
	usedAvatars = []
	sts_crs = StudentRegisteredCourses.objects.filter(courseID=currentCourse)
	for st_cs in sts_crs:
		usedAvatars.append(st_cs.avatarImage)
	print(usedAvatars)
	
	avatarPath = []	
	for name in glob.glob('static/images/avatars/*'):
		name = name.replace("\\","/")
		namec = '/'+name
		if not namec in usedAvatars:
			avatarPath.append(name)
			print(name)
		
	#Find all used avatars
	usedAvatars = []
	sts_crs = StudentRegisteredCourses.objects.filter(courseID=currentCourse)
	for st_cs in sts_crs:
		usedAvatars.append(st_cs.avatarImage)
	
	context_dict["avatarPaths"] = zip(range(1,len(avatarPath)+1), avatarPath)

