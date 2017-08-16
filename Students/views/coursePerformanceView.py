'''
Created on Feb 22, 2017

'''
from django.shortcuts import render
from Students.models import StudentChallenges, Student, StudentActivities, StudentRegisteredCourses
from Instructors.models import Challenges, Courses, Activities
from time import strftime
import datetime
from django.db.models import Q

from django.contrib.auth.decorators import login_required

@login_required
def CoursePerformance(request):
    # Request the context of the request.
 
    context_dict = { }
    
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username             
  
    if 'ID' in request.GET:
        optionSelected = request.GET['ID']
        context_dict['ID'] = request.GET['ID']
    else:
        optionSelected = 0
        
    # check if course was selected
    if not 'currentCourseID' in request.session:
        context_dict['course_Name'] = 'Not Selected'
        context_dict['course_notselected'] = 'Please select a course'
    else:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        print('current course:'+str(currentCourse))
        context_dict['course_Name'] = currentCourse.courseName
        
        studentId = Student.objects.get(user=request.user)   
        st_crs = StudentRegisteredCourses.objects.get(studentID=studentId,courseID=currentCourse)
        context_dict['avatar'] = st_crs.avatarImage          
                   
        # Activity and Challenges
        assignmentID = []
        assignmentName = []
        assignmentType = []
        assignmentTime = []
        assignmentGrade = []
        assignmentGradeTotal = []
        assignmentFeedback = []
    
        # Default time is the time that is saved in the database when challenges are created with no dates assigned (AH)
        defaultTime = (datetime.datetime.strptime("12/31/2999 11:59:59 PM" ,"%m/%d/%Y %I:%M:%S %p"))
        currentTime = strftime("%Y-%m-%d %H:%M:%S")
        
        stud_activities = StudentActivities.objects.filter(studentID=studentId, courseID=currentCourse).filter(Q(timestamp__lt=currentTime) | Q(timestamp=defaultTime))
        for sa in stud_activities:
            assignmentID.append(sa.studentActivityID)
            a = Activities.objects.get(pk=sa.activityID.activityID)
            assignmentName.append(a.activityName)
            assignmentType.append("Activity")
            assignmentTime.append(sa.timestamp)
            assignmentGrade.append(sa.activityScore)
            assignmentGradeTotal.append(sa.activityScore)
            assignmentFeedback.append(sa.instructorFeedback)
                
      
        # Select if startTime is less than(__lt) currentTime (AH)
        challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=True, isVisible=True).filter(Q(startTimestamp__lt=currentTime) | Q(startTimestamp=defaultTime))
        
        for challenge in challenges:  
            if StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse, challengeID = challenge) :
                
                sChallenges = StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse, challengeID = challenge)
                latestSC = StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse, challengeID = challenge).latest('startTimestamp')

                gradeID  = []
                       
                for sc in sChallenges:
                    gradeID.append(sc.testScore)

                gMax = (max(gradeID))
                
                assignmentID.append(challenge.challengeID)
                assignmentName.append(challenge.challengeName)
                assignmentType.append("Challenge")
                assignmentTime.append(latestSC.endTimestamp)
                assignmentGrade.append(gMax)
                assignmentGradeTotal.append(latestSC.testTotal)
                assignmentFeedback.append("")
        
             
        # The range part is the index numbers.
        context_dict['challenge_range'] = zip(range(1,len(assignmentID)+1),assignmentID,assignmentName,assignmentType, assignmentTime,assignmentGrade, assignmentGradeTotal, assignmentFeedback)
        context_dict['challenge_range'] = reversed(sorted(context_dict['challenge_range'], key = lambda t: t[4]))
    
    return render(request,'Students/CoursePerformance.html', context_dict)