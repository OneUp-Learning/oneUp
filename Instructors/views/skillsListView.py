'''
Created on Apr 7, 2014

@author: dichevad
'''
from django.template import RequestContext
from django.shortcuts import render
from Instructors.models import Skills, Courses, CoursesSkills 
from django.contrib.auth.decorators import login_required

@login_required
def skillsListView(request):
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
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
          
        skill_ID = []      
        skill_Name = []
        #skill_Author = []         
        
        cskills = CoursesSkills.objects.filter(courseID=currentCourse)
        for sk in cskills:
            skill_ID.append(sk.skillID.skillID) 

            skills = Skills.objects.filter(skillID=sk.skillID.skillID)
            for s in skills:
                skill_Name.append(s.skillName)
            #skill_Author.append(item.skillAuthor)
                        
            # The range part is the index numbers.
        context_dict['skill_range'] = zip(range(1,cskills.count()+1),skill_ID,skill_Name)

    return render(request,'Instructors/SkillsList.html', context_dict)
