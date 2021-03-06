'''
Created on Oct 15, 2014

@author: Swapna
'''
from django.shortcuts import render
from Instructors.models import Skills, Courses, CoursesSkills
from Students.models import Student, StudentRegisteredCourses
from Students.views.utils import studentInitialContextDict
from django.contrib.auth.decorators import login_required
from Badges.models import CourseConfigParams
from oneUp.ckeditorUtil import config_ck_editor

@login_required
def CourseInformation(request):
    
    context_dict, currentCourse = studentInitialContextDict(request)
    
    if currentCourse.courseDescription != "":
        context_dict['course_Description'] = currentCourse.courseDescription
                    
    skill_ID = []      
    skill_Name = []
    
    cskills = CoursesSkills.objects.filter(courseID=currentCourse)
    for sk in cskills:
        skill_ID.append(sk.skillID.skillID) 

        skills = Skills.objects.filter(skillID=sk.skillID.skillID)
        for s in skills:
            skill_Name.append(s.skillName)
                    
    context_dict['skill_range'] = zip(range(1,cskills.count()+1),skill_ID,skill_Name)
    context_dict['ckeditor'] = config_ck_editor()
        
    return render(request,'Students/CourseInformation.html', context_dict)
