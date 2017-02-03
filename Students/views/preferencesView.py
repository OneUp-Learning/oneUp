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
from Students.models import StudentConfigParams,Student
from django.contrib.auth.models import User

@login_required
def preferencesView(request):

   
    context_dict = { }  
    ccparams =[]
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
        sID = Student.objects.get(user=request.user)
        context_dict['avatar'] = sID.avatarImage        
        print(sID)
        
    # check if course was selected
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
        print(currentCourse)
#         ccparams = CourseConfigParams.objects.get(pk=int(request.POST['courseID']))
        c_ccparams = CourseConfigParams.objects.filter(courseID=currentCourse)
        
#         for i in c_ccparams:
#             ccparams = i
        if len(c_ccparams) > 0:
            ccparams = c_ccparams[0] 
            print('ccparams', ccparams)
            context_dict['studCanChangeBadgeVis']=ccparams.studCanChangeBadgeVis
            context_dict['studCanChangeLeaderboardVis']=ccparams.studCanChangeLeaderboardVis
            context_dict['studCanChangeClassSkillsVis']=ccparams.studCanChangeClassSkillsVis
            print("ccparams.studCanChangeBadgeVis:",ccparams.studCanChangeBadgeVis)
#             print("inloop")
#             print(ccparams)
#         print("outloop")
#         print(ccparams)
        else:
            context_dict['course_Name'] = 'Not Selected'
        
#         ccparams = CourseConfigParams.objects.filter(courseID=currentCourse, studCanChangeBadgeVis)
        
        
#         studentChallenges = StudentChallenges.objects.filter(studentID=studentId, courseID=currentCourse, challengeID = request.GET['challengeID'])
        
    else:
        context_dict['course_Name'] = 'Not Selected' 
    
    if request.POST:
        
#         ccparams = CourseConfigParams.objects.get(pk=int(request.POST['courseID']))
#         
        # There is an existing topic, edit it
        if request.POST['scpID']:
            scparams = StudentConfigParams.objects.get(pk=int(request.POST['scpID']))
            print(request.POST['scpID'])
            print("--xxxxxx-")
            print(scparams,scparams.courseID,scparams.studentID,scparams.displayBadges,scparams.displayLeaderBoard,scparams.displayClassSkills)
            
        else:
            # Create new Config Parameters
            scparams = StudentConfigParams()
            scparams.courseID = currentCourse
            studentID = Student.objects.get(user=request.user)
            scparams.studentID = studentID
#          print(studentID)
            #scparams.studentID = User.objects.filter(userID=request.POST['userID'],courseID=currentCourse)
        if ccparams.studCanChangeBadgeVis:  
            scparams.displayBadges = "displayBadges" in request.POST
            
        if ccparams.studCanChangeLeaderboardVis:  
            scparams.displayLeaderBoard = "displayLeaderBoard" in request.POST
            
        if ccparams.studCanChangeClassSkillsVis:  
            scparams.displayClassSkills = "displayClassSkills" in request.POST
                
        scparams.displayClassAverage = "displayClassAverage" in request.POST 
        scparams.displayClassRanking = "displayClassRanking" in request.POST     
        scparams.save()
        print(scparams,scparams.courseID,scparams.studentID,scparams.displayBadges,scparams.displayLeaderBoard,scparams.displayClassSkills)
        return redirect('/oneUp/students/StudentCourseHome',"","")
       
    #################################
    #  get request
    #  For the fields that are not visbile because the instructor did not choose to be used for the course. you can pass false so null exceptions are not created
    else:
        
        scparamsList = StudentConfigParams.objects.filter(courseID=currentCourse, studentID=sID)
            
        if len(scparamsList) > 0:
            scparams = scparamsList[0]   
            context_dict['scpID'] = scparams.scpID
            context_dict["displayBadges"]=scparams.displayBadges
            context_dict["displayLeaderBoard"]=scparams.displayLeaderBoard
            context_dict["displayClassAverage"]=scparams.displayClassAverage
            context_dict["displayClassSkills"]=scparams.displayClassSkills
            context_dict["displayClassRanking"]=scparams.displayClassRanking
            
        return render(request,'Students/Preferences.html', context_dict)

     

