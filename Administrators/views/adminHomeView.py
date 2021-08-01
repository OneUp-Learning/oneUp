'''
Created on Sep 10, 2016
Last Updated Sep 20, 2016

'''
from django.template import RequestContext
from django.shortcuts import render
from django.contrib.auth.models import User
from Instructors.models import Courses, Universities, InstructorToUniversities, UniversityCourses
from django.contrib.auth.decorators import login_required, user_passes_test
from oneUp.decorators import adminsCheck
from oneupsdk import get_course_term, get_course_name

@login_required
@user_passes_test(adminsCheck, login_url='/oneUp/home', redirect_field_name='')
def adminHome(request):

    context_dict = {}
    context_dict["logged_in"] = request.user.is_authenticated
    if request.user.is_authenticated:
        context_dict["username"] = request.user.username

    # Create Administrators List (AH)
    administrators = User.objects.filter(groups__name='Admins')
    print("Admins:", administrators)
    isTeacher = []
    
    
    for user in administrators:
        if User.objects.filter(username=user.username, groups__name='Teachers').exists():
            isTeacher.append(True)
        else:
            isTeacher.append(False)
            
 
    print(isTeacher)
    context_dict['administrators'] = list(zip(administrators, isTeacher))
    

    # Create Instructors List (AH)
    instructors = User.objects.filter(groups__name='Teachers')

    print("Instructors:", instructors)
    isAdmin = []
    
    uniInstructors = InstructorToUniversities.objects.all() 
    universityID = []
    instructorID = []
    
    for user in instructors:
        if User.objects.filter(username=user.username, groups__name='Admins').exists():
            isAdmin.append(True)
        else:
            isAdmin.append(False)
            
    for u in uniInstructors:
        universityID.append(u.universityID)
        instructorID.append(u.instructorID)
        
    #add university this instructor list 
    instructList = [ 'No University' for i in range(len(instructors)) ]  
    for i in range(0, len(instructors)):      
        for p in range(0, len(instructorID)):
            if( instructors[i] == instructorID[p] ):
                instructList[i] = universityID[p].universityName  
                
              
    print(isAdmin)
    context_dict['instructors'] = list(zip(instructors, instructList, isAdmin))
    #university list with all the university with course 
   
    uniList_ = [ 'No University' for i in range(len(universityID)+1) ] 
    for i in range(0, len(universityID)):
        uniList_[i] = universityID[i].universityName
      
    uniList = [ uniList_[i] for i in range(len(uniList_)) ] 
    #remove duplicates 
    for u in range( len(uniList)-1, -1, -1):
        for i in range( 0, len( uniList)-1):
            if( (i != u ) and (uniList[i] == uniList[u]) ):
                uniList.pop( u )
            
    context_dict['instructUniversityList'] = list(uniList)
    # Create Courses List (AH)
    
    courses = Courses.objects.all()   
    print("Courses:", courses)
    course_ID = []
    course_Name = []
    
    uniCourse = UniversityCourses.objects.all() 
    universityID = []
    uni_courseID = []
    
    for u in uniCourse:
        universityID.append(u.universityID)
        uni_courseID.append(u.courseID)
        
    for c in courses:
        course_ID.append(c.courseID)
        course_Name.append(c.courseName)
      
    #add university to the course list 
    courseList = [ 'No University' for i in range(len(courses)) ]  
    for i in range(0, len(course_Name)):      
        for p in range(0, len(uni_courseID)):
            if( course_ID[i] == uni_courseID[p].courseID ):
                courseList[i] = universityID[p].universityName

    context_dict['courses'] = list( zip(
        range(1, len(courses)+1), course_ID, courseList, course_Name))
    #university list with all the university with course 
   
    uniList_ = [ 'No University' for i in range(len(universityID)+1) ] 
    for i in range(0, len(universityID)):
        uniList_[i] = universityID[i].universityName
      
    uniList = [ uniList_[i] for i in range(len(uniList_)) ] 
    #remove duplicates 
    for u in range( len(uniList)-1, -1, -1):
        for i in range( 0, len( uniList)-1):
            if( (i != u ) and (uniList[i] == uniList[u]) ):
                uniList.pop( u )
            
    context_dict['universites'] = Universities.objects.all()
    
 
    context_dict['courseUniversityList'] = list( (uniList ) )
    

    return render(request, 'Administrators/adminHome.html', context_dict)
