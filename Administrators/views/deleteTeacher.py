
from django.template import RequestContext
from django.shortcuts import render, redirect
from Instructors.models import Instructors, InstructorRegisteredCourses
from django.contrib.auth.models import User

def teacherDeleteView(request):
    
        context_dict = { }
        context_dict["logged_in"]=request.user.is_authenticated()
        if request.user.is_authenticated():
            user = request.user
        context_dict["username"]=user.username
        
        # Retrieved all instructors and append them to the context dict
        instructors = User.objects.filter(groups__name='Teachers')
        instructor_Username = []
        instructor_FName = []
        instructor_LName = []
        instructor_isStaff = []
        instructor_isActive = []
        instructor_isSuper = []
        instructor_dateJoin = []
        
        for i in instructors:
            instructor_Username.append(i.username)
            instructor_FName.append(i.first_name)
            instructor_LName.append(i.last_name)
            instructor_isStaff.append(i.is_staff)
            instructor_isActive.append(i.is_active)
            instructor_isSuper.append(i.is_superuser)
            instructor_dateJoin.append(i.date_joined)
            
        
        context_dict['instructors'] = zip(range(1, len(instructors)+1), instructor_Username, instructor_FName, instructor_LName,
                                          instructor_isStaff, instructor_isActive, instructor_isSuper, instructor_dateJoin)
        print(instructors)

        # If request is GET then return the context dict
        if request.method=='GET':
            return render(request,'Administrators/deleteTeacher.html',context_dict)
        else: # Method is POST then delete selected course(AH)
            if request.POST['instructorToDelete']:
                instructor = User.objects.get(username=request.POST['instructorToDelete'])
                print("Deleted:", instructor)            
                instructor.delete()
                
            return redirect('/oneUp/administrators/adminHome.html')
            