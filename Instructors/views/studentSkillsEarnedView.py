'''
Created on August 25, 2015

@author: Alex 
'''
from django.template import RequestContext
from django.shortcuts import render

from Instructors.models import Skills, Courses, CoursesSkills
from Students.models import StudentCourseSkills, StudentChallengeQuestions, StudentChallenges, Student
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required

@login_required
def studentSkillsEarned(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict = { }
    
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username
    
    # check if course was selected
    if not 'currentCourseID' in request.session:
        context_dict['course_Name'] = 'Not Selected'
        context_dict['course_notselected'] = 'Please select a course'
    else:
        currentCourseId = int(request.session['currentCourseID'])
        currentCourse = Courses.objects.get(pk=currentCourseId)
        context_dict['course_Name'] = currentCourse.courseName
        
        user = User.objects.filter(username=request.GET['userID'])
        studentId = Student.objects.filter(user=user)
        
        for u in studentId:
            name = str(u.user.first_name) + ' ' + str(u.user.last_name)
        context_dict['name'] = name
        
        skill_ID = []      
        skill_Name = []         
        skill_Points = []
        
        count = 0;
        
        course_skills = CoursesSkills.objects.filter(courseID=currentCourseId)
        for s in course_skills:
            skillRecords = StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=studentId, skillID = s.skillID)
            skillPoints =0;

            for sRecord in skillRecords:
                skillPoints += sRecord.skillPoints
            
            skillId= s.skillID.skillID
            skillName = Skills.objects.get(pk=skillId).skillName
            
            if skillPoints > 0:
                skill_ID.append(skillId)
                skill_Name.append(skillName)
                skill_Points.append(skillPoints)
                count +=1

        context_dict['skill_range'] = zip(range(1,count+1),skill_ID,skill_Name,skill_Points)

    return render(request,'Instructors/StudentSkillsEarned.html', context_dict)