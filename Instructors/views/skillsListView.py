'''
Created on Apr 7, 2014

@author: dichevad
'''
from django.shortcuts import render
from Instructors.models import Skills, CoursesSkills 
from Instructors.views.utils import initialContextDict
from django.contrib.auth.decorators import login_required

@login_required
def skillsListView(request):
    context_dict, currentCourse = initialContextDict(request)

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
