#  Ranga
#  11/12/2015

from Students.models import Student, StudentChallenges, StudentCourseSkills, StudentRegisteredCourses
from django.contrib.auth.decorators import login_required


def classAverChallengeScore(course, challenge):

    count = 0
    totalChall = 0
    # Students from the current class
    stud_course = StudentRegisteredCourses.objects.filter(courseID=course, studentID__isTestStudent=False)

    for sc in stud_course:
        # get all attempts for this student for this challenge
        attempts = StudentChallenges.objects.filter(studentID=sc.studentID, courseID=course, challengeID=challenge)
        if attempts.exists():
            
            chall_score = []
            max_score = 0
            for attempt in attempts:
                max_score = max(max_score, attempt.getScore())

            totalChall += max_score
            count += 1

    if (count > 0):
        avgChall = totalChall/count
    else:
        avgChall = 0

    return avgChall

# Skills


def skillClassAvg(skill, course):

    users = []
    # Students from the current class
    stud_course = StudentRegisteredCourses.objects.filter(courseID=course)
    for sc in stud_course:
        users.append(sc.studentID)

    totalSkillPoints = 0
    userCount = 0

    for user in users:
        if StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=user, skillID=skill):
            skillRecords = StudentCourseSkills.objects.filter(
                studentChallengeQuestionID__studentChallengeID__studentID=user, skillID=skill)
            for sRecord in skillRecords:
                print("ssskillPoints"+str(sRecord.skillPoints))
                # total skill points for this student for this skill
                totalSkillPoints += sRecord.skillPoints
                # skillClassAvgcount +=1  # DD
            userCount += 1
    if userCount == 0:
        classAvgSkill = 0
    else:
        classAvgSkill = totalSkillPoints/userCount
    print("avgskill"+str(classAvgSkill))
    return classAvgSkill
