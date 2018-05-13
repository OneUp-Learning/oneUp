from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from Instructors.views.utils import initialContextDict
from Badges.models import VirtualCurrencyRuleInfo, VirtualCurrencyCustomRuleInfo, Badges
from Students.models import StudentRegisteredCourses, Student, StudentBadges, StudentFile, User
from Badges.systemVariables import logger
from pytz import reference
from pip._vendor.requests.certs import where


@login_required
def addBadgeManuallyView(request):
    context_dict, course = initialContextDict(request)
    if 'currentCourseID' in request.session:
        if request.method == 'GET':
            students = StudentRegisteredCourses.objects.filter(courseID = course).order_by("studentID__user__last_name")
            studentID = []
            studentName= []
            for studentobj in students:
                studentID.append(studentobj.studentID)
                studentName.append(studentobj.studentID.user.get_full_name())
            
            badges = Badges.objects.filter(courseID = course)
            customRules = [r for r in badges if hasattr(r, 'ruleID')]
            
            ##get thecustom made badge
            allBadgeID = []
            allBadgeDecripName = []
            for badge in customRules:
                allBadgeID.append(badge.badgeID)
                allBadgeDecripName.append(badge.badgeDescription)
            
            
            context_dict['students'] = (zip(studentID, studentName))#, key=lambda tup: tup[1])
                                              
            context_dict['badges'] = list(zip(allBadgeID, allBadgeDecripName))
            return render(request, 'Badges/AddBadgeManually.html', context_dict)
        elif request.method == 'POST':
            logger.debug(request.POST)
            
            ##grab the student in the most indirect way possible, by first getting the User by the userID
            ##then grab the student object by using that studentiD
            studentID = User.objects.filter(username=request.POST['userID']).first()
            student = Student.objects.filter(user=studentID).first()
    
            ##create the badge in the student section
            ##save it in
            studentBadge = StudentBadges()
            referencedBadge = Badges.objects.filter(badgeID=request.POST['badgeID']).first()
            print(student)
            print(request.POST['badgeID'])
            print(referencedBadge)
            studentBadge.studentID = student
            studentBadge.badgeID = referencedBadge
            studentBadge.save()
                
                                
            
            return redirect('AddBadgeManually.html')
            