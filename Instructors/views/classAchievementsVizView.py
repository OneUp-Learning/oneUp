
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Instructors.models import Courses, Challenges, CoursesSkills
from Students.models import Student, StudentChallenges, StudentCourseSkills, StudentRegisteredCourses, StudentChallengeQuestions
    
@login_required
def classAchievementsViz(request):
 
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

        serious = 0
        warmUp = 0
        skills = 0
        if 'serious' in request.GET:
            serious = 1
            context_dict['serious']= 1
        elif 'warmUp' in request.GET:
            warmUp = 1
            context_dict['warmUp']= 1
        else:
            skills = 1
            context_dict['skills']= 1   
            
        st_crs = StudentRegisteredCourses.objects.filter(courseID=currentCourse)                
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
    
        else:
            # visualize challenges               
            allChallengGrades = []
                                
            #Displaying the list of challenges from database
            if serious:
                challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=True)
            else:
                challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=False) 
                                 
            for challenge in challenges:
                userScores = []
                userEarliestScores = []
                maxTestScores = []
                mediumTestScores = []
                minTestScores = []
                userNames = []
                challNames = [] 
                           
                if StudentChallenges.objects.filter(courseID=currentCourse, challengeID = challenge):   
                    
                    for student in students:
                        if StudentChallenges.objects.filter(studentID=student, courseID=currentCourse, challengeID = challenge):
                            studentChall = StudentChallenges.objects.filter(studentID=student, courseID=currentCourse, challengeID = challenge) 
                            latestChall = StudentChallenges.objects.filter(studentID=student, courseID=currentCourse, challengeID = challenge).latest('startTimestamp')
                            earliestChall =  StudentChallenges.objects.filter(studentID=student, courseID=currentCourse, challengeID = challenge).earliest('startTimestamp')
                            
                            challNames.append(challenge.challengeName)
                            userLatestScore = latestChall.testScore
                            userEarliestScore = earliestChall.testScore
                            userScores.append(userLatestScore)
                            userEarliestScores.append(userEarliestScore)
                            userNames.append(str(student.user.first_name+' '+student.user.last_name))
                            userGradeID  = []
                        
                            sumScores = 0
                            for scr in studentChall:
                                userGradeID.append(int(scr.testScore))
                                sumScores += int(scr.testScore)
                            
                            maxTestScores.append(max(userGradeID))
                            minTestScores.append(min(userGradeID))
                            mediumTestScores.append(sumScores/len(studentChall))
    
                            allChallengGrades.append(zip(challNames, userNames, maxTestScores,mediumTestScores, minTestScores ))        
            
            context_dict['challengesRange'] = zip(range(1,len(allChallengGrades)+1),allChallengGrades)
            context_dict['challengesCount'] = challenges.count()
                                
    return render(request,'Instructors/ClassAchievementsViz.html', context_dict)
