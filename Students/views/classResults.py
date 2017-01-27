from Students.models import Student, StudentChallenges, StudentCourseSkills
                                      
def classAverChallengeScore(course,resource, resourceIndicator):  

    user = Student.objects.all()
    num_users = user.count() 
    count = 0
    totalChall = 0
    
    for i in range(0, num_users):
        if StudentChallenges.objects.filter(studentID=user[i],courseID=course, challengeID=resource): 
            studentChallenges = StudentChallenges.objects.filter(studentID=user[i],courseID=course, challengeID=resource).latest('startTimestamp')
            count +=1
            totalChall += studentChallenges.testScore
    if (count > 0):
        avgChall= totalChall/count
    else:
        avgChall = 0
    
    print ("avgchall"+str(avgChall))                                    
    return avgChall
#Skills - Nondef SkillAvg
def skillClassAvg(resource, resourceIndicator):  

    user = Student.objects.all()
    skillnum_users = user.count()
    print ("skilluserCount"+str(skillnum_users))  
    print("resource"+str(resource))
    totalSkills = 0
    skillClassAvgcount = 0
    
    for i in range(0, skillnum_users):
        if StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=user[i], skillID = resource): 
            skillRecords = StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=user[i], skillID = resource)
            for sRecord in skillRecords:
                print ("ssskillPoints"+str(sRecord.skillPoints))
                totalSkills += sRecord.skillPoints
                skillClassAvgcount +=1      
    if skillClassAvgcount == 0:
        classAvgSkill = 0
    else:
        classAvgSkill= totalSkills/skillClassAvgcount
    print ("avgskill"+str(classAvgSkill))                                     
    return classAvgSkill


#Skills - def SkillTotal
def defSkillClassTotal(resource):  

    user = Student.objects.all()
    skillnum_users = user.count()
    #print ("skilluserCount"+str(skillnum_users))  
    #print("resource"+str(resource))
    totalSkills = 0
    #skillClassAvgcount = 0
    
    for i in range(0, skillnum_users):
        if StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=user[i], skillID = resource): 
            skillRecords = StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=user[i], skillID = resource)
            for sRecord in skillRecords:
                print ("defskillPoints"+str(sRecord.skillPoints))
                totalSkills += sRecord.skillPoints
                
    print ("totalSkills"+str(totalSkills))                                     
    return totalSkills

#Skills - Nondef SkillTotal
def skillClassTotal(resource):  

    user = Student.objects.all()
    skillnum_users = user.count()
    #print ("skilluserCount"+str(skillnum_users))  
    #print("resource"+str(resource))
    totalSkills = 0
    #skillClassAvgcount = 0
    
    for i in range(0, skillnum_users):
        if StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=user[i], skillID = resource): 
            skillRecords = StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=user[i], skillID = resource)
            for sRecord in skillRecords:
                print ("ssskillPoints"+str(sRecord.skillPoints))
                totalSkills += sRecord.skillPoints
                
    print ("totalSkills"+str(totalSkills))                                     
    return totalSkills

def classAverSkillPoints(skillId, courseId):

        total = 0.0
        stNum = 0
        average = 0.0
        #if tagString is not null or empty
        if challengeId and courseId: 
            
            studentChallenges = StudentChallenges.objects.filter(courseID=courseId, skillID=skillId)
            
            for studChall in studentChallenges:
                print (studChall)
                total = total +  studChall.testScore
                stNum = stNum + 1 
                
            average = total/stNum
        
        return average