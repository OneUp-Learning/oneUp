'''
Created on Oct 15, 2014

@author: Swapna
'''
from django.template import RequestContext
from django.shortcuts import render
from Instructors.models import Skills, Courses, CoursesSkills
from Students.models import Student, StudentRegisteredCourses

def CourseInformation(request):
    context_dict = { }
    context_dict["logged_in"]=request.user.is_authenticated()
    if request.user.is_authenticated():
        context_dict["username"]=request.user.username       
        
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
        context_dict['course_Description'] = currentCourse.courseDescription
        student = Student.objects.get(user=request.user)   
        st_crs = StudentRegisteredCourses.objects.get(studentID=student,courseID=currentCourse)
        context_dict['avatar'] = st_crs.avatarImage          
                
        skill_ID = []      
        skill_Name = []         
        
        cskills = CoursesSkills.objects.filter(courseID=currentCourse)
        for sk in cskills:
            skill_ID.append(sk.skillID.skillID) 

            skills = Skills.objects.filter(skillID=sk.skillID.skillID)
            for s in skills:
                skill_Name.append(s.skillName)
            #skill_Author.append(item.skillAuthor)
                        
            # The range part is the index numbers.
        context_dict['skill_range'] = zip(range(1,cskills.count()+1),skill_ID,skill_Name)
        
    else:
        context_dict['course_Name'] = 'Not Selected'       
        
    return render(request,'Students/CourseInformation.html', context_dict)
