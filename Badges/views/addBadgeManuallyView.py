from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from Instructors.views.utils import initialContextDict
from Badges.events import register_event
from Badges.enums import Event
from Badges.models import VirtualCurrencyRuleInfo, VirtualCurrencyCustomRuleInfo, BadgesInfo, BadgesVCLog
from Students.models import StudentRegisteredCourses, Student, StudentBadges, StudentFile, User
from Badges.systemVariables import logger
from pytz import reference
from Instructors.views.whoAddedVCAndBadgeView import create_badge_vc_log_json
import json

@login_required
def addBadgeManuallyView(request):
    context_dict, course = initialContextDict(request)
    if 'currentCourseID' in request.session:
        if request.method == 'GET':
            students = StudentRegisteredCourses.objects.filter(courseID = course).order_by("studentID__user__last_name")
            
            students_details = []
            test_students_details = []
            for studentobj in students:
                name = studentobj.studentID.user.get_full_name()
                if studentobj.studentID.isTestStudent:
                    test_students_details.append({'id': studentobj.studentID, 'name': f'{name} (Test Student)'})
                else:
                    students_details.append({'id': studentobj.studentID, 'name': name})
                
            test_students_details = sorted(test_students_details, key=lambda x: x['name'].casefold())
            
            badges = BadgesInfo.objects.filter(courseID = course)
            
            manual_badges = []
            automatic_badges = []
            periodic_badges = []
            for badge in badges:
                if badge.manual == True:
                    manual_badges.append({'id': badge.badgeID, 'name': badge.badgeName, 'description': badge.badgeDescription})
                elif badge.manual == False and badge.isPeriodic == False:
                    automatic_badges.append({'id': badge.badgeID, 'name': badge.badgeName, 'description': badge.badgeDescription})
                elif badge.isPeriodic == True:
                    periodic_badges.append({'id': badge.badgeID, 'name': badge.badgeName, 'description': badge.badgeDescription})
                
            context_dict['students'] = students_details
            context_dict['test_students'] = test_students_details
            context_dict['manual_badges'] = manual_badges
            context_dict['automatic_badges'] = automatic_badges
            context_dict['periodic_badges'] = periodic_badges
            
            student_badges_details = []
            for student in students_details:
                studentBadges = StudentBadges.objects.filter(studentID=student['id'], badgeID__courseID=course)
                if studentBadges.exists():
                    badges = []
                    for badge in studentBadges:
                        badges.append({'id': badge.studentBadgeID, 'name': badge.badgeID.badgeName, 'image': badge.badgeID.badgeImage})
                    student_badges_details.append({'student': student, 'badges': badges})
            
            for student in test_students_details:
                studentBadges = StudentBadges.objects.filter(studentID=student['id'], badgeID__courseID=course)
                if studentBadges.exists():
                    badges = []
                    for badge in studentBadges:
                        badges.append({'id': badge.studentBadgeID, 'name': badge.badgeID.badgeName, 'image': badge.badgeID.badgeImage})
                    student_badges_details.append({'student': student, 'badges': badges})
            
            context_dict['student_badges'] = student_badges_details

            # studentNames = []
            # studentAwardedBadgesZipList = []
            
            # ##for each student object in students models
            # for studentObjects in students:
            #         ##append each full student name to the student names list
            #         studentNames.append(studentObjects.studentID.user.get_full_name())
                    
            #         ##filter the student badges objects, by selecting where studentID matches studentObjets
            #         ##studentID
            #         studentBadges = StudentBadges.objects.filter(studentID = studentObjects.studentID, badgeID__courseID=course)
                    
                    
            #         ##we must blank this out on each iteration so it will load in only what maches the studentID
            #         studentBadgeID = []
            #         studentBadgeName = []
            #         studentBadgeImage = []
            #         if studentBadges == None:##if we dont have any badges match our students, load in blank list
            #             studentAwardedBadgesZipList.append(list(zip(studentBadgeID, studentBadgeName, studentBadgeImage)))
            #         else:##otherwise for each student badgeobject, grab the id name and image    
            #             for studentBadge in studentBadges:
            #                 badgeInfo = BadgesInfo.objects.get(badgeID = studentBadge.badgeID.badgeID)
                            
            #                 studentBadgeID.append(studentBadge.studentBadgeID)
            #                 studentBadgeName.append(studentBadge.badgeID.badgeName)
            #                 studentBadgeImage.append(studentBadge.badgeID.badgeImage)
            #             #print(studentBadgeImage)
            #             ##at the end of  the for, append the things into the list
            #             studentAwardedBadgesZipList.append(list(zip(studentBadgeID, studentBadgeName, studentBadgeImage)))
                        
            # ##append to the context dictionary, the student names, and student awardedbadges list
            # context_dict['studentBadges'] = list(zip(studentNames, studentAwardedBadgesZipList))

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

                studentAddBadgeLog = BadgesVCLog()
                studentAddBadgeLog.courseID = course
                log_data = create_badge_vc_log_json(request.user, studentBadge, "Badge", "Manual")
                studentAddBadgeLog.log_data = json.dumps(log_data)
                studentAddBadgeLog.save()

                # Register even that a badge was earned
                register_event(Event.badgeEarned, request, student, referencedBadge.pk)
                
            ##we are sent checkboxes to remove from students    
            if 'checkboxes' in request.POST:
                checkboxes = request.POST.getlist('checkboxes')
                for badge in checkboxes:
                    StudentBadges.objects.filter(studentBadgeID=badge).delete()
                    
            return redirect('AddBadgeManually.html')
            
