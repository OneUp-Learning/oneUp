
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from Instructors.models import Challenges, CoursesSkills
from Instructors.views.utils import initialContextDict
from Students.models import StudentChallenges, StudentCourseSkills, StudentRegisteredCourses, StudentGoalSetting
from oneUp.decorators import instructorsCheck

from Badges.enums import Goal
from Badges import systemVariables
from Students.views import goalCreateView, goalsListView  
from Students.views.goalsListView import goalsList
from datetime import datetime, date, time, timedelta
    
@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')
def classAchievementsViz(request):

    context_dict, currentCourse = initialContextDict(request)
    
    serious = 0
    warmUp = 0
    skills = 0
    goals = 0
    if 'serious' in request.GET:
        serious = 1
        context_dict['serious']= 1
    elif 'warmUp' in request.GET:
        warmUp = 1
        context_dict['warmUp']= 1
    elif 'goals' in request.GET:    #4.4.19 - JC
        goals = 1
        context_dict['goals'] = 1
    else:
        skills = 1
        context_dict['skills']= 1   
        
    st_crs = StudentRegisteredCourses.objects.filter(courseID=currentCourse).exclude(studentID__isTestStudent=True)                
    students = []                                         
    for st_c in st_crs:
        students.append(st_c.studentID)     # all students in the course
            
    if  skills:
        # visualize skills 
        skillNames = [] 
        allStudSkillPoints = []  
                             
        # for each skill, for each student
        c_skills = CoursesSkills.objects.filter(courseID=currentCourse)            
        for c_skill in c_skills: 
            skill = c_skill.skillID
            skillNames.append(skill.skillName)
            userNames = []
            userSkillPoints = []            

            for student in students: 
                userNames.append(str(student.user.first_name+' '+student.user.last_name))                    
                studentSkill = StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=student, skillID=skill)
                if not studentSkill:
                    userSkillPoints.append(0)    
                else:
                    totalPointsSkill = 0
                    chall_question_IDs = []
                    print(studentSkill)
                    for s_skill in studentSkill:
                        print('s_skill')
                        print(s_skill)
                        chall_question_IDs.append(s_skill.studentChallengeQuestionID.questionID.questionID)  # all takings of contributing questions
                    
                    print('chall_question_IDs: ')
                    print(chall_question_IDs)    
                    q_set = set(chall_question_IDs)
                    print('q_set: ')
                    print(q_set)                         
                    q_answering = []    
                    for q in q_set:
                        #filter all answers of q
                        for s_skill in studentSkill:
                            if s_skill.studentChallengeQuestionID.questionID.questionID == q:
                                q_answering.append(s_skill.skillPoints)     
                        
                        print('max(q_answers): '+str(max(q_answering)))# adding the max of skill points from all answering of the same question q                                                    
                        totalPointsSkill +=max(q_answering)
                    
                    print('totalPointsSkill: '+str(totalPointsSkill))    
                    userSkillPoints.append(totalPointsSkill)     
       
            allStudSkillPoints.append(zip(userNames, userSkillPoints ))
            print(userNames)
            print(userSkillPoints)
                
        context_dict['skillsRange'] = zip(range(1,len(skillNames)+1),skillNames)
        context_dict['pointsRange'] = zip(range(1,len(skillNames)+1),allStudSkillPoints)
        context_dict['skillsCount'] = len(skillNames)
        print(skillNames)
        print(str(len(skillNames)))
        
        return render(request,'Instructors/ClassSkillsViz.html', context_dict)
    
    elif goals:
        
        # visualize challenges               
        allGoals = []
                            
        #Displaying the list of challenges from database
                             
        for student in students:
#            userScores = []
#            userEarliestScores = []
            goals_Created = []
            goals_Completed = []
            goals_Failed = []
            user_Names = []
            completed = 0
            failed = 0
            created = 0
                       
            goals = StudentGoalSetting.objects.filter(courseID=currentCourse, studentID=student)
            glview = goalsListView
            
            for g in goals:
                created += 1
                progressPercent = glview.calculateProgress(g.progressToGoal, g.goalType, g.courseID, g.studentID, g.targetedNumber)
                endDate = g.timestamp + timedelta(days=7)
                if (glview.goalStatus(progressPercent, endDate) == "Completed"):
                    completed += 1
                if (glview.goalStatus(progressPercent, endDate) == "Failed"):
                    failed += 1
                    
            user_Names.append(str(student.user.first_name+' '+student.user.last_name))
            print (user_Names)
            print (created)      
            goals_Created.append(created)
            print (completed)
            goals_Completed.append(completed)
            print(failed)
            goals_Failed.append(failed)
            
                
            allGoals.append(zip(user_Names, goals_Created,goals_Completed,goals_Failed ))  
            
        context_dict['goalsRange'] = zip(range(1,len(allGoals)+1),allGoals)
        context_dict['goalsCount'] = goals.count()   
        
        return render(request,'Instructors/ClassGoalsViz.html', context_dict)
                    
    else:
        # visualize challenges               
        allChallengGrades = []
                            
        #Displaying the list of challenges from database
        if serious:
            challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=True)
        else:
            challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=False) 
                             
        for challenge in challenges:
#            userScores = []
#            userEarliestScores = []
            maxTestScores = []
            mediumTestScores = []
            minTestScores = []
            userNames = []
            challNames = [] 
                       
            if StudentChallenges.objects.filter(courseID=currentCourse, challengeID = challenge):   
                
                for student in students:
                    if StudentChallenges.objects.filter(studentID=student, courseID=currentCourse, challengeID = challenge):
                        studentChall = StudentChallenges.objects.filter(studentID=student, courseID=currentCourse, challengeID = challenge) 

#                         latestChall = StudentChallenges.objects.filter(studentID=student, courseID=currentCourse, challengeID = challenge).latest('startTimestamp')
#                         earliestChall =  StudentChallenges.objects.filter(studentID=student, courseID=currentCourse, challengeID = challenge).earliest('startTimestamp')
#                                                 
#                         if challenge.isGraded:    # serious challenge, add the adjustment + curve
#                             userLatestScore = latestChall.getScore()
#                             userEarliestScore = earliestChall.getScore()
#                         else:
#                             userLatestScore = latestChall.testScore         # warmup challenge
#                             userEarliestScore = earliestChall.testScore
#                                                                                         
#                         userScores.append(userLatestScore)
#                         userEarliestScores.append(userEarliestScore)
                                               
                        userNames.append(str(student.user.first_name+' '+student.user.last_name))
                        challNames.append(challenge.challengeName)
                        userGradeID  = []                    
                        sumScores = 0
                        for scr in studentChall:
                            if challenge.isGraded:    # serious challenge, add the adjustment + curve
                                score = scr.getScore()
                            else:
                                score = scr.testScore         # warmup challenge
                            
                            #userGradeID.append(int(scr.testScore))
                            userGradeID.append(int(score))
                            sumScores += int(score)
                        
                        maxTestScores.append(max(userGradeID))
                        minTestScores.append(min(userGradeID))
                        mediumTestScores.append(sumScores/len(studentChall))

                        allChallengGrades.append(zip(challNames, userNames, maxTestScores,mediumTestScores, minTestScores ))        
        
        context_dict['challengesRange'] = zip(range(1,len(allChallengGrades)+1),allChallengGrades)
        context_dict['challengesCount'] = challenges.count()
                                
    return render(request,'Instructors/ClassAchievementsViz.html', context_dict)

