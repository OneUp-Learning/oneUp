from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from Instructors.models import Skills, Courses, CoursesSkills
from Instructors.views.utils import initialContextDict
from oneUp.decorators import instructorsCheck  

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def skillsCreateView(request):
    context_dict, currentCourse = initialContextDict(request)

    string_attributes = ['skillName'];
    
    if request.POST:
        
        # There is an existing skill, edit it
        if request.POST['skillID']:
            skill = Skills.objects.get(pk=int(request.POST['skillID']))
        else:
            # Create new skill
            skill = Skills()
            
        # Copy all strings from POST to database object.
        for attr in string_attributes:
            setattr(skill,attr,request.POST[attr])

        # get the author
        if request.user.is_authenticated:
            skill.skillAuthor = request.user.username
        else:
            skill.skillAuthor = ""
            
        skill.save()
        
        if not request.POST['skillID']:
            # add the new skill to current course
            courseSkill = CoursesSkills()
            courseSkill.courseID = currentCourse
            courseSkill.skillID = skill
            courseSkill.save()


                
    #################################
    #  get request
    else:
        if 'skillID' in request.GET:
            context_dict['skillID'] = request.GET['skillID']
            skill = Skills.objects.get(pk=int(request.GET['skillID']))
            for attr in string_attributes:
                context_dict[attr]=getattr(skill,attr)
       
    return render(request,'Instructors/SkillsCreate.html', context_dict)

