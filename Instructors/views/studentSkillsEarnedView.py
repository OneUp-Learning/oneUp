'''
Created on August 25, 2015

@author: Alex 
'''
from django.shortcuts import render

from Instructors.models import Skills, CoursesSkills
from Instructors.views.utils import initialContextDict
from Students.models import StudentCourseSkills, Student
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required, user_passes_test
from oneUp.decorators import instructorsCheck 

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')   
def studentSkillsEarned(request):
 
    context_dict, currentCourse = initialContextDict(request)
    
    user = User.objects.filter(username=request.GET['userID'])
    studentId = Student.objects.filter(user=user)
    
    for u in studentId:
        name = str(u.user.first_name) + ' ' + str(u.user.last_name)
    context_dict['name'] = name
    
    skill_ID = []      
    skill_Name = []         
    skill_Points = []
    
    count = 0;
    
    course_skills = CoursesSkills.objects.filter(courseID=currentCourse)
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