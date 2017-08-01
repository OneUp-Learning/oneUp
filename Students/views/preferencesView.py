'''
Created on Sep 15, 2016
#Updated The order of the fields to match the templates
@author: Vendhan
'''
from django.template import RequestContext
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Instructors.models import Skills, Courses, CoursesSkills, Topics
from Badges.models import CourseConfigParams
from Students.models import StudentConfigParams,Student, StudentRegisteredCourses
from Students.views.utils import studentInitialContextDict
from django.contrib.auth.models import User

@login_required
def preferencesView(request):

    context_dict,currentCourse = studentInitialContextDict(request)
   
#     context_dict = { }  
#     ccparams =[]
#     context_dict["logged_in"]=request.user.is_authenticated()
#     if request.user.is_authenticated():
#         context_dict["username"]=request.user.username
#         
#     # check if course was selected
#     if 'currentCourseID' in request.session:
#         currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
#         context_dict['course_Name'] = currentCourse.courseName
#         student = Student.objects.get(user=request.user)   
#         st_crs = StudentRegisteredCourses.objects.get(studentID=student,courseID=currentCourse)
#         context_dict['avatar'] = st_crs.avatarImage          
        

    if 'currentCourseID' in request.session:    
        
        c_ccparams = CourseConfigParams.objects.filter(courseID=currentCourse)
        
        if len(c_ccparams) > 0:
            ccparams = c_ccparams[0] 
            print('ccparams', ccparams)
            context_dict['studCanChangeBadgeVis']=ccparams.studCanChangeBadgeVis
            context_dict['studCanChangeLeaderboardVis']=ccparams.studCanChangeLeaderboardVis
            context_dict['studCanChangeClassSkillsVis']=ccparams.studCanChangeClassSkillsVis
            context_dict['studCanChangeclassAverageVis']=ccparams.studCanChangeclassAverageVis    
                    
        student = context_dict['student']   
    
    if request.POST:
        
        if request.POST['scpID']:
            scparams = StudentConfigParams.objects.get(pk=int(request.POST['scpID']))
            
        else:
            #studentID = Student.objects.get(user=request.user)
            scparams = StudentConfigParams.objects.get(courseID=currentCourse, studentID=student)

#          print(studentID)
            #scparams.studentID = User.objects.filter(userID=request.POST['userID'],courseID=currentCourse)
        if ccparams.studCanChangeBadgeVis:  
            scparams.displayBadges = "displayBadges" in request.POST
            
        if ccparams.studCanChangeLeaderboardVis:  
            scparams.displayLeaderBoard = "displayLeaderBoard" in request.POST
            
        if ccparams.studCanChangeClassSkillsVis:  
            scparams.displayClassSkills = "displayClassSkills" in request.POST

        if ccparams.studCanChangeclassAverageVis:  
            scparams.displayClassAverage = "displayClassAverage" in request.POST
                                
        # scparams.displayClassAverage = "displayClassAverage" in request.POST 
        scparams.displayClassRanking = "displayClassRanking" in request.POST     
        scparams.save()
        print(scparams,scparams.courseID,scparams.studentID,scparams.displayBadges,scparams.displayLeaderBoard,scparams.displayClassSkills)
        return redirect('/oneUp/students/StudentCourseHome',"","")
       
    #################################
    #  get request
    #  For the fields that are not visbile because the instructor did not choose to be used for the course. you can pass false so null exceptions are not created
    else:
        
        scparamsList = StudentConfigParams.objects.filter(courseID=currentCourse, studentID=student)
            
        if len(scparamsList) > 0:
            scparams = scparamsList[0]   
            context_dict['scpID'] = scparams.scpID
            context_dict["displayBadges"]=scparams.displayBadges
            context_dict["displayLeaderBoard"]=scparams.displayLeaderBoard
            context_dict["displayClassAverage"]=scparams.displayClassAverage
            context_dict["displayClassSkills"]=scparams.displayClassSkills
            context_dict["displayClassRanking"]=scparams.displayClassRanking
            
        return render(request,'Students/Preferences.html', context_dict)

     

