'''
Created on Sep 14, 2016

'''
from django.shortcuts import render
from Instructors.models import Courses
from Students.models import StudentConfigParams,Student,StudentRegisteredCourses, StudentBadges
from Instructors.views.announcementListView import createContextForAnnouncementList
from Instructors.views.upcommingChallengesListView import createContextForUpcommingChallengesList
from Instructors.views.dynamicLeaderboardView import generateLeaderboards

from Badges.enums import Event
from Badges.models import  CourseConfigParams
from Badges.events import register_event
from django.contrib.auth.decorators import login_required
from Students.views.utils import studentInitialContextDict

from Students.views.avatarView import checkIfAvatarExist

from Badges.periodicVariables import studentScore, TimePeriods

@login_required
def StudentCourseHome(request):
	context_dict = { }
	context_dict["logged_in"]=request.user.is_authenticated
	if request.user.is_authenticated:
		context_dict["username"]=request.user.username
		sID = Student.objects.get(user=request.user)

	if request.POST:
		request.session['currentCourseID'] = request.POST['courseID']
		context_dict['course_id']=request.POST['courseID']
		context_dict['is_test_student'] = sID.isTestStudent
		if sID.isTestStudent:
			context_dict["username"]="Test Student"
	
	if request.GET:
		request.session['currentCourseID'] = request.GET['courseID']
		context_dict['course_id']=request.GET['courseID']
		context_dict['is_test_student'] = sID.isTestStudent
		if sID.isTestStudent:
			context_dict["username"]="Test Student"
			
	if 'currentCourseID' in request.session:
		currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
		context_dict['ccparams'] = CourseConfigParams.objects.get(courseID=currentCourse)
		context_dict = createContextForAnnouncementList(currentCourse, context_dict, True)
		context_dict = createContextForUpcommingChallengesList(currentCourse, context_dict)
		context_dict['course_Name'] = currentCourse.courseName
		context_dict['is_test_student'] = sID.isTestStudent
		if sID.isTestStudent:
			context_dict["username"]="Test Student"
		context_dict['course_id'] = currentCourse.courseID
		st_crs = StudentRegisteredCourses.objects.get(studentID=sID,courseID=currentCourse)
		context_dict['avatar'] =  st_crs.avatarImage  
		context_dict['course_Bucks'] = str(st_crs.virtualCurrencyAmount)  
		
		context_dict['leaderboardRange'] = generateLeaderboards(currentCourse, True)  
		context_dict['courseId']=currentCourse.courseID

		# Progress Bar
		_, xp, _, _, _, _, earnedSeriousChallengePoints, _, earnedActivityPoints, _, totalPointsSeriousChallenges, totalPointsActivities = studentScore(
		sID, currentCourse, 0, TimePeriods.timePeriods[1503], 0, result_only=True, gradeWarmup=False, gradeSerious=False, seriousPlusActivity=False, context_dict=context_dict)

		context_dict['studentXP_range'] = xp
		# PROGRESS BAR
		# this is the max points that the student can earn in this course
		progressBarTotalPoints = context_dict['ccparams'].progressBarTotalPoints

		currentEarnedPoints = earnedSeriousChallengePoints + earnedActivityPoints
		currentTotalPoints = totalPointsSeriousChallenges + totalPointsActivities
		missedPoints = currentTotalPoints - currentEarnedPoints
		if not currentTotalPoints == 0:
			projectedEarnedPoints = round(
				currentEarnedPoints * progressBarTotalPoints/currentTotalPoints)
		else:
			projectedEarnedPoints = 0
		remainingPointsToEarn = progressBarTotalPoints - currentTotalPoints

		context_dict['currentEarnedPoints'] = currentEarnedPoints
		context_dict['missedPoints'] = missedPoints
		context_dict['projectedEarnedPoints'] = projectedEarnedPoints
		context_dict['progressBarTotalPoints'] = progressBarTotalPoints
		context_dict['remainingPointsToEarn'] = remainingPointsToEarn

		   
		scparamsList = StudentConfigParams.objects.filter(courseID=currentCourse, studentID=sID)   
		##GGM determine if student has leaderboard enabled

		studentConfigParams = StudentConfigParams.objects.get(courseID=currentCourse, studentID=sID)
		context_dict['displayLeaderBoard'] = studentConfigParams.displayLeaderBoard
		 
		if len(scparamsList) > 0:
			scparams = scparamsList[0]
			context_dict["displayBadges"]=scparams.displayBadges
			context_dict["displayLeaderBoard"]=scparams.displayLeaderBoard
			context_dict["displayClassAverage"]=scparams.displayClassAverage
			context_dict["displayClassSkills"]=scparams.displayClassSkills
			
		
		
		context_dict['badgesInfo'] = studentBadges(currentCourse)
		context_dict['studentBadges'] = studentBadges(currentCourse, student=sID)
	
	#Trigger Student login event here so that it can be associated with a particular Course
	register_event(Event.userLogin, request, None, None)
	print("User Login event was registered for the student in the request")
	
	if context_dict['ccparams'].displayStudentStartPageSummary == True:
		return render(request,'Students/StudentCourseHomeSummary.html', context_dict)
	else:          
		return render(request,'Students/StudentCourseHome.html', context_dict)        


def studentBadges(currentCourse, student=None):
	
	# Check if there are students in this course
	st_crs = StudentRegisteredCourses.objects.filter(courseID=currentCourse).exclude(studentID__isTestStudent=True)

	if st_crs:
		if currentCourse:
			ccparams = CourseConfigParams.objects.get(courseID=currentCourse)
			
			badgeId = [] 
			studentBadgeID=[]
			studentID=[]
			badgeID=[]
			badgeName=[]
			badgeImage = []
			avatarImage =[]
			studentUser = []

			students = []     
			if student is None:                                    
				for st_c in st_crs:
					students.append(st_c.studentID) # all students in the course
			else:
				students.append(student)     
			
			#Displaying the list of challenges from database
			badges = StudentBadges.objects.filter(badgeID__courseID=currentCourse).order_by('-timestamp')
			
			for badge in badges:
				if badge.studentID in students:
					studentBadgeID.append(badge.studentBadgeID)
					studentID.append(badge.studentID)
					badgeID.append(badge.badgeID)
					badgeName.append(badge.badgeID.badgeName)
					badgeImage.append(badge.badgeID.badgeImage)
					st_crs = StudentRegisteredCourses.objects.get(studentID=badge.studentID,courseID=currentCourse)       
					avatarImage.append(checkIfAvatarExist(st_crs))          
								
			return list(zip(range(1,ccparams.numBadgesDisplayed+1),studentBadgeID,studentID,badgeID, badgeName, badgeImage,avatarImage))
		
	return None 
	