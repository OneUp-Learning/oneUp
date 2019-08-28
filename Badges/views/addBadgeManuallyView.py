from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from Instructors.views.utils import initialContextDict
from Badges.models import VirtualCurrencyRuleInfo, VirtualCurrencyCustomRuleInfo, BadgesInfo
from Students.models import StudentRegisteredCourses, Student, StudentBadges, StudentFile, User
from Badges.systemVariables import logger
from pytz import reference


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
                name = studentobj.studentID.user.get_full_name()
                if studentobj.studentID.isTestStudent:
                    name += " (Test Student)"
                studentName.append(name)
            
            badges = BadgesInfo.objects.filter(courseID = course , manual=True)
            customRules = [r for r in badges]
            
            ##get thecustom made badge
            allBadgeID = []
            allBadgeDecripName = []
            for badge in customRules:
                allBadgeID.append(badge.badgeID)
                allBadgeDecripName.append(badge.badgeDescription)
                
            context_dict['students'] = list(zip(studentID, studentName))
            context_dict['badges'] = list(zip(allBadgeID, allBadgeDecripName))
            
            
            
            studentNames = []
            studentAwardedBadgesZipList = []
            
            ##for each student object in students models
            for studentObjects in students:
                    ##append each full student name to the student names list
                    studentNames.append(studentObjects.studentID.user.get_full_name())
                    
                    ##filter the student badges objects, by selecting where studentID matches studentObjets
                    ##studentID
                    studentBadges = StudentBadges.objects.filter(studentID = studentObjects.studentID)
                    
                    
                    ##we must blank this out on each iteration so it will load in only what maches the studentID
                    studentBadgeID = []
                    studentBadgeName = []
                    studentBadgeImage = []
                    if studentBadges == None:##if we dont have any badges match our students, load in blank list
                        studentAwardedBadgesZipList.append(list(zip(studentBadgeID, studentBadgeName, studentBadgeImage)))
                    else:##otherwise for each student badgeobject, grab the id name and image    
                        for studentBadge in studentBadges:
                            badgeInfo = BadgesInfo.objects.get(badgeID = studentBadge.badgeID.badgeID)
                            if(badgeInfo.manual):
                                studentBadgeID.append(studentBadge.studentBadgeID)
                                studentBadgeName.append(studentBadge.badgeID.badgeName)
                                studentBadgeImage.append(studentBadge.badgeID.badgeImage)
                        #print(studentBadgeImage)
                        
                        ##at the end of  the for, append the things into the list
                        studentAwardedBadgesZipList.append(list(zip(studentBadgeID, studentBadgeName, studentBadgeImage)))
                        
            ##append to the context dictionary, the student names, and student awardedbadges list
            context_dict['studentBadges'] = list(zip(studentNames, studentAwardedBadgesZipList))

            return render(request, 'Badges/AddBadgeManually.html', context_dict)
        elif request.method == 'POST':
            logger.debug(request.POST)
            
            if 'userID' in request.POST:
                
                ##grab the student in the most indirect way possible, by first getting the User by the userID
                ##then grab the student object by using that studentiD
                studentID = User.objects.filter(username=request.POST['userID']).first()
                student = Student.objects.filter(user=studentID).first()
        
                ##create the badge in the student section
                ##save it in
                studentBadge = StudentBadges()
                referencedBadge = BadgesInfo.objects.filter(badgeID=request.POST['badgeID']).first()
                print(student)
                print(request.POST['badgeID'])
                print(referencedBadge)
                studentBadge.studentID = student
                studentBadge.badgeID = referencedBadge 
                studentBadge.save()
                
            ##we are sent checkboxes to remove from students    
            if 'checkboxes' in request.POST:
                checkboxes = request.POST.getlist('checkboxes')
                for badge in checkboxes:
                    StudentBadges.objects.filter(studentBadgeID=badge).delete()
                    
            return redirect('AddBadgeManually.html')
            