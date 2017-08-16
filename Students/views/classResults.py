#  Ranga
#  11/12/2015

from Students.models import Student, StudentChallenges, StudentCourseSkills, StudentRegisteredCourses
                                      
def classAverChallengeScore(course,challenge):  

    count = 0
    totalChall = 0
    
    users = [] 
    # Students from the current class
    stud_course = StudentRegisteredCourses.objects.filter(courseID=course)
    for sc in stud_course:
        users.append(sc.studentID)
    
    
    for user in users:
        if StudentChallenges.objects.filter(studentID=user,courseID=course, challengeID=challenge): 
            # get all attempts for this student for this challenge
            studentChallenges = StudentChallenges.objects.filter(studentID=user,courseID=course, challengeID=challenge)
            chall_score = []
            for attempt in studentChallenges:
                chall_score.append(attempt.testScore) 

            totalChall += max(chall_score)
            count +=1
            
    if (count > 0):
        avgChall= totalChall/count
    else:
        avgChall = 0
    
    print ("avgchall  "+str(avgChall))                                    
    return avgChall

#Skills 
def skillClassAvg(skill, course):  

    users = [] 
    # Students from the current class
    stud_course = StudentRegisteredCourses.objects.filter(courseID=course)
    for sc in stud_course:
        users.append(sc.studentID)
      
    totalSkillPoints = 0
    userCount = 0
    
    for user in users:
        if StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=user, skillID = skill): 
            skillRecords = StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=user, skillID = skill)
            for sRecord in skillRecords:
                print ("ssskillPoints"+str(sRecord.skillPoints))
                totalSkillPoints += sRecord.skillPoints  # total skill points for this student for this skill
                #skillClassAvgcount +=1  # DD 
            userCount +=1    
    if userCount == 0:
        classAvgSkill = 0
    else:
        classAvgSkill= totalSkillPoints/userCount
    print ("avgskill"+str(classAvgSkill))                                     
    return classAvgSkill

