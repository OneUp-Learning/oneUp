'''
Created on Nov 14, 2016

@author: Joel Evans
'''

from django.shortcuts import render, redirect
from django.http import JsonResponse
import glob
from Badges.models import CourseConfigParams
from Students.models import Student, StudentRegisteredCourses,StudentCustomAvatar
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
		if 'avatar' in request.POST:
			avatarImage = request.POST['avatar'] # The Chosen Avatar Image Name
			print("avatar image: "+str(avatarImage))
	
			st_crs = StudentRegisteredCourses.objects.get(studentID=sID,courseID=currentCourse)	 
			st_crs.avatarImage = avatarImage
			st_crs.save()
		
			context_dict['avatar'] = avatarImage	
		return redirect('/oneUp/students/StudentCourseHome', context_dict)

	return render(request, 'Students/Avatar.html', context_dict)

def extractPaths(context_dict, currentCourse, sID): #function used to get the names from the file locaiton
	usedAvatars = []
	student = StudentRegisteredCourses.objects.get(courseID=currentCourse, studentID = sID)
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
	
	#Check to make sure the students avatar still exisit if not chagne to default
	checkIfAvatarExist(student)
		
	avatarPath.sort()
	context_dict["avatarPaths"] = zip(range(1,len(avatarPath)+1), avatarPath)

def checkIfAvatarExist(student):
	c = student.courseID
	useCustom = CourseConfigParams.objects.get(courseID = c).useCustomAvatar

	avatars = glob.glob('static/images/avatars/*')
	defaultAvatar = '/static/images/avatars/anonymous.png'
	if not useCustom:		
		studentAvatarPath = student.avatarImage
		studentAvatarPath = studentAvatarPath[1:]
		if studentAvatarPath in avatars:
			return student.avatarImage
		else:
			student.avatarImage = defaultAvatar #change the students avatar to the default
			student.save()		
		
	else:
		s = student.studentID
		st_ava_list = StudentCustomAvatar.objects.filter(studentID = s)
		if len(st_ava_list)==0:
			st_ava = StudentCustomAvatar()
			st_ava.studentID = s            
			st_ava.save()
		else:
			st_ava = st_ava_list[0]   		    
	                  
		return st_ava.image         
	return defaultAvatar 
	
def checkAvatar(request):
	''' This view is called by an ajax function to check for avatar duplicates'''
	print("Here***")
	context_dict,currentCourse = studentInitialContextDict(request)

	if request.POST:
		avatar = request.POST.get('avatarstr')
		print("avatar:", avatar)
		if StudentRegisteredCourses.objects.filter(courseID=currentCourse, avatarImage=avatar).exists():
			return JsonResponse({"success": False, "message":"A student has already selected that avatar"})
		
	return JsonResponse({"success": True, "message": 'Great success!'})
