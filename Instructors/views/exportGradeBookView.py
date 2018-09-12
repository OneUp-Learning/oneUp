'''
Created on Apr 5, 2018

@author: omar
'''

from django.shortcuts import render
import csv
from django.http import HttpResponse
from Instructors.models import Courses, Challenges, Activities
from Instructors.views.utils import initialContextDict
from Students.models import StudentChallenges, StudentRegisteredCourses, StudentActivities
from django.contrib.auth.decorators import login_required

@login_required
def exportGradebook(request):
    context_dict, currentCourse = initialContextDict(request)

    if request.method == 'GET':
        return render(request,'Instructors/ExportGradebook.html', context_dict)
    
    if request.method == 'POST':        
       
        selectedCategories = request.POST.getlist('selected')
        
        if selectedCategories:
            
            #boolean for selected categories
            serious = False 
            warmup = False 
            graded = False
            notGraded = False 
            
            for s in selectedCategories:
                s=str(s)
                if s=="serious":
                    serious = True
                elif s=="warmup":
                    warmup = True
                elif s=="graded":
                    graded = True
                elif s=="notGraded":
                    notGraded=True
                
            # check if course was selected
            if not 'currentCourseID' in request.session:
                context_dict['course_Name'] = 'Not Selected'
                context_dict['course_notselected'] = 'Please select a course'
            else:
                currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
                context_dict['course_Name'] = currentCourse.courseName
                
                first_Name = []      
                last_Name = []     
                allgrades = []
                gradeTotal = []
                allActivityGrade = []
                
                try:
                    optionSelected = request.POST.get("dropdown")
                except:
                    optionSelected = 1
                            
                if serious and warmup:
                    challenges = Challenges.objects.filter(courseID=currentCourse, isVisible=True)
                elif serious:
                    challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=True,  isVisible=True)
                elif warmup:
                    challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=False,  isVisible=True)
                 
                if serious or warmup:   
                    num_challs = challenges.count()
                
                if graded and notGraded:
                    activities = Activities.objects.filter(courseID=currentCourse)
                elif graded:
                    activities = Activities.objects.filter(courseID=currentCourse, isGraded=True)
                elif notGraded:
                    activities = Activities.objects.filter(courseID=currentCourse, isGraded=False)
                
                users = [] 
                #Displaying the list of students from the current class
                stud_course = StudentRegisteredCourses.objects.filter(courseID=currentCourse).exclude(studentID__isTestStudent=True)
                for sc in stud_course:
                    users.append(sc.studentID)

                # Create the HttpResponse object with CSV header.
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="exportedGradeBook.csv"'
            
                writer = csv.writer(response)
                 
                for u in users:
                    first_Name.append(u.user.first_name)
                    last_Name.append(u.user.last_name)
                
                header = []
                header.append('Name')
                header.append('Total')
                
                if serious or warmup:
                    for c in challenges:
                        header.append(c.challengeName)
                if graded or notGraded:  
                    for activity in activities:
                        header.append(activity.activityName)
                
                # write header to CSV file     
                writer.writerow(header)
                
                #for i in range(0, num_users):  
                for user in users:
                    grade = []
                    gradeLast = []
                    gradeFirst = []
                    gradeMax = []
                    gradeMin = []
                    number  = []
                    numberLast  = []
                    numberFirst  = []
                    numberMax  = []
                    numberMin  = []
                    sc_user = []
                    sc_chall = []
                    activityGradeList = []
                    
                    if warmup or serious:
                        for j in range(0, num_challs):  
                            if StudentChallenges.objects.filter(studentID=user, courseID=currentCourse, challengeID = challenges[j]) :
                                
                                sChallenges = StudentChallenges.objects.filter(studentID=user, courseID=currentCourse, challengeID = challenges[j])
                                latestSC = StudentChallenges.objects.filter(studentID=user, courseID=currentCourse, challengeID = challenges[j]).latest('startTimestamp')
                                earliestSC =StudentChallenges.objects.filter(studentID=user, courseID=currentCourse, challengeID = challenges[j]).earliest('startTimestamp')
                                
                                gradeLast.append(latestSC.getScoreWithBonus())
                                gradeFirst.append(earliestSC.getScoreWithBonus())
                                numberLast.append(latestSC.getScoreWithBonus())
                                numberFirst.append(earliestSC.getScoreWithBonus())
                                
                                sc_user.append(user)
                                sc_chall.append(challenges[j].challengeID)
                                gradeID  = []
                                
                                for sc in sChallenges:
                                    gradeID.append(sc.getScoreWithBonus())
                                gradeMax.append(("%0.2f" %max(gradeID)))
                                gradeMin.append(("%0.2f" %min(gradeID)))
                                numberMax.append(max(gradeID))
                                numberMin.append(min(gradeID))
                                
                            else:
                                gradeLast.append(0.00)
                                gradeFirst.append(0.00)
                                gradeMax.append(0.00)
                                gradeMin.append(0.00)
                                sc_user.append(0)
                                sc_chall.append(0)
                                numberLast.append(0)
                                numberFirst.append(0)
                                numberMax.append(0)
                                numberMin.append(0)
                    
                    if graded or notGraded:
                        totalActivityGrade = 0        
                        for activity in activities:
                            
                            if StudentActivities.objects.filter(courseID=currentCourse, studentID=user, activityID=activity):
                                activityGrade = StudentActivities.objects.get(courseID=currentCourse, studentID=user, activityID=activity).getScoreWithBonus()
                                activityGradeList.append(str(activityGrade))
                                print(user, activityGrade)
                            else:
                                activityGrade = 0
                                activityGradeList.append(0.00)
                            
                            totalActivityGrade += activityGrade
                    
                    if warmup or serious:
                        if optionSelected == '1':
                            grade = gradeMax
                            number = numberMax
                        elif optionSelected == '2':
                            grade = gradeMin
                            number = numberMin
                        elif optionSelected == '3':
                            grade = gradeLast
                            number = numberLast
                        elif optionSelected == '4':
                            grade = gradeFirst
                            number = numberFirst
                        else:
                            grade = gradeMax
                            number = numberMax
                            
                        allgrades.append(grade)
                            
                    if (warmup or serious) and (graded or notGraded):
                        total = sum(number) + totalActivityGrade
                    elif warmup or serious:
                        total = sum(number)
                    elif graded or notGraded:
                        total = totalActivityGrade
                        
                    
                    gradeTotal.append(("%0.2f" %total))
                    if graded or notGraded:
                        allActivityGrade.append(activityGradeList)
                
                        #context_dict['activityGrade_range'] = zip(range(0,len(allActivityGrade)),allActivityGrade)
                
                if (warmup or serious) and (graded or notGraded):
                    for first_Name,last_Name,allgrades,allActivityGrade, gradeTotal in sorted(list(zip(first_Name,last_Name,allgrades,allActivityGrade, gradeTotal)), key=lambda tup: tup[1]):
                        
                        # write data to CSV file
                        writer.writerow([first_Name+' '+last_Name,gradeTotal]+allgrades+allActivityGrade)
        
                elif warmup or serious:
                    for first_Name,last_Name,allgrades, gradeTotal in sorted(list(zip(first_Name,last_Name,allgrades, gradeTotal)), key=lambda tup: tup[1]):
                        
                        # write data to CSV file
                        writer.writerow([first_Name+' '+last_Name,gradeTotal]+allgrades)
                        
                elif graded or notGraded:
                    for first_Name,last_Name,allActivityGrade, gradeTotal in sorted(list(zip(first_Name,last_Name,allActivityGrade, gradeTotal)), key=lambda tup: tup[1]):
                        
                        # write data to CSV file
                        writer.writerow([first_Name+' '+last_Name,gradeTotal]+allActivityGrade)
                        
                return response
        
    return render(request,'Instructors/ExportGradebook.html', context_dict)
    #return render(request,'oneUp/instructors/classAchievements', context_dict)
    
