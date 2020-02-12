'''
Created on Sep 14, 2016

'''
from django.shortcuts import render
from django.http import JsonResponse

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

from collections import defaultdict
import json

@login_required
def StudentCourseHome(request):
	context_dict, currentCourse = studentInitialContextDict(request)

	if context_dict['is_test_student']:
		context_dict["username"] = "Test Student"
	
	context_dict['course_Bucks'] = str(context_dict['student_registered_course'].virtualCurrencyAmount)  

	context_dict = createContextForAnnouncementList(currentCourse, context_dict, True)
	context_dict = createContextForUpcommingChallengesList(currentCourse, context_dict)

	progress_data = progress_bar_data(currentCourse, context_dict['ccparams'], for_student=context_dict['student'])

	context_dict['currentEarnedPoints'] = progress_data['currentEarnedPoints']
	context_dict['missedPoints'] = progress_data['missedPoints']
	context_dict['projectedEarnedPoints'] = progress_data['projectedEarnedPoints']
	context_dict['progressBarTotalPoints'] = progress_data['progressBarTotalPoints']
	context_dict['remainingPointsToEarn'] = progress_data['remainingPointsToEarn']

	context_dict['studentXP_range'] = progress_data['xp']
	context_dict['totalWCEarnedPoints'] = progress_data['data']['totalWCEarnedPoints']
	context_dict['totalWCPossiblePoints'] = progress_data['data']['totalWCPossiblePoints']

	context_dict["challengeClassmates"] = progress_data['data']["challengeClassmates"] 
	context_dict["numOfDuelSent"] = progress_data['data']["numOfDuelSent"] 
	context_dict["numOfDuelAccepted"] = progress_data['data']["numOfDuelAccepted"] 
	context_dict["numOfDuelWon"] = progress_data['data']["numOfDuelWon"] 
	context_dict["numOfDuelLost"] = progress_data['data']["numOfDuelLost"] 
	context_dict["numOfCalloutSent"] = progress_data['data']["numOfCalloutSent"] 
	context_dict["numOfCalloutRequest"] = progress_data['data']["numOfCalloutRequest"] 
	context_dict["numOfCalloutWon"] = progress_data['data']["numOfCalloutWon"]
	context_dict["numOfCalloutLost"] = progress_data['data']["numOfCalloutLost"]
	
	context_dict['badgesInfo'] = studentBadges(currentCourse)
	context_dict['studentBadges'] = studentBadges(currentCourse, student=context_dict['student'])
	context_dict['leaderboardRange'] = generateLeaderboards(currentCourse, True) 
	
	#Trigger Student login event here so that it can be associated with a particular Course
	register_event(Event.userLogin, request, None, None)
	print("User Login event was registered for the student in the request")
	
	if context_dict['ccparams'].displayStudentStartPageSummary == True:
		return render(request,'Students/StudentCourseHomeSummary.html', context_dict)
	else:          
		return render(request,'Students/StudentCourseHome.html', context_dict)        

@login_required
def progressBarData(request):

	context_dict, currentCourse = studentInitialContextDict(request)

	response = defaultdict(int)
	if request.method == 'GET':
		# If these options are none then use the ccparams options
		class_scores = None
		metric_average = None
		# Use the options that were passed through the request
		if 'class_scores' in request.GET and 'metric_average' in request.GET:
			class_scores = json.loads(request.GET.get('class_scores', 'true'))
			metric_average = json.loads(request.GET.get('metric_average', 'false'))

		response = progress_bar_data(currentCourse, context_dict['ccparams'], class_scores=class_scores, metric_average=metric_average, for_student=context_dict['student'])
	else:
		response['status'] = "failure"

	return JsonResponse(response)

def progress_bar_data(current_course, ccparams, class_scores=None, metric_average=None, for_student=None):
	''' Gets the progress bar data for a class or student.
		If for_student is passed, class_scores needs to be set to False or 
		the course configuration variable should be False.

		This will also return the studentScore results for "for_student" in the key "data"
	'''

	response = defaultdict(int)
	# Determine how to process the data for the progress bar
	if class_scores is None and metric_average is None:
		class_scores = ccparams.progressBarGroupUsed
		metric_average = ccparams.progressBarGroupAverage
	
	# this is the max points that the student can earn in this course
	progressBarTotalPoints = ccparams.progressBarTotalPoints

	if class_scores:
		students = StudentRegisteredCourses.objects.filter(courseID= current_course, studentID__isTestStudent=False)
		for student in students:
			# Get latest data
			data = studentScore(student.studentID, current_course, 0, TimePeriods.timePeriods[1503], 0, result_only=True)
		
			response['xp'] += data['xp']
			if for_student == student.studentID:
				response['data'] = data

			currentEarnedPoints = data['earnedSeriousChallengePoints'] + data['earnedActivityPoints']
			currentTotalPoints = data['totalPointsSeriousChallenges'] + data['totalPointsActivities']
			missedPoints = currentTotalPoints - currentEarnedPoints
			
			if not currentTotalPoints == 0:
				projectedEarnedPoints = round(
					currentEarnedPoints * progressBarTotalPoints/currentTotalPoints)
			else:
				projectedEarnedPoints = 0
			remainingPointsToEarn = progressBarTotalPoints - currentTotalPoints

			response['currentEarnedPoints'] += currentEarnedPoints
			response['missedPoints'] += missedPoints
			response['projectedEarnedPoints'] += projectedEarnedPoints
			response['remainingPointsToEarn'] += remainingPointsToEarn

		if metric_average and students:
			response['xp'] = response['xp'] / len(students)
			response['currentEarnedPoints'] = response['currentEarnedPoints'] / len(students)
			response['missedPoints'] = response['missedPoints'] / len(students)
			response['projectedEarnedPoints'] = response['projectedEarnedPoints'] / len(students)
			response['remainingPointsToEarn'] = response['remainingPointsToEarn'] / len(students)
		
		response['progressBarTotalPoints'] = progressBarTotalPoints
		
	else:
		# Get latest data
		data = studentScore(for_student, current_course, 0, TimePeriods.timePeriods[1503], 0, result_only=True)
	
		response['xp'] = data['xp']
		response['data'] = data

		currentEarnedPoints = data['earnedSeriousChallengePoints'] + data['earnedActivityPoints']				
		currentTotalPoints = data['totalPointsSeriousChallenges'] + data['totalPointsActivities']
		missedPoints = currentTotalPoints - currentEarnedPoints

		if not currentTotalPoints == 0:
			projectedEarnedPoints = round(
				currentEarnedPoints * progressBarTotalPoints/currentTotalPoints)
		else:
			projectedEarnedPoints = 0
		remainingPointsToEarn = progressBarTotalPoints - currentTotalPoints

		response['currentEarnedPoints'] = currentEarnedPoints
		response['missedPoints'] = missedPoints
		response['projectedEarnedPoints'] = projectedEarnedPoints
		response['progressBarTotalPoints'] = progressBarTotalPoints
		response['remainingPointsToEarn'] = remainingPointsToEarn

	response['status'] = "success"

	return response

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
	