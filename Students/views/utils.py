from Instructors.views.utils import initialContextDict
from Students.models import Student, StudentRegisteredCourses, StudentConfigParams, StudentPlayerType
from django.contrib.auth.models import User
import glob

def studentInitialContextDict(request):    
    context_dict, currentCourse = initialContextDict(request)
    
    if 'userID' in request.GET:    
        stud = User.objects.get(username=request.GET['userID'])
        student = Student.objects.get(user=stud)
        context_dict["is_teacher"] = True
        context_dict['is_test_student'] = student.isTestStudent
    else:
        context_dict["is_student"] = True
        student = Student.objects.get(user=request.user)
        context_dict['is_test_student'] = student.isTestStudent
      
    st_crs = StudentRegisteredCourses.objects.get(studentID=student,courseID=currentCourse)
    context_dict['student'] = student
    context_dict['student_registered_course'] = st_crs
    
    context_dict['avatar'] = checkIfAvatarExist(st_crs)
        
    studentConfigParams = StudentConfigParams.objects.get(courseID=currentCourse, studentID=context_dict['student'])
    context_dict['scparams'] = studentConfigParams
    
    ###If adapation used for the student, update gamification settings to use PlayerType profiles
    if context_dict['ccparams'].adaptationUsed:
        studentPlayerType = StudentPlayerType.objects.filter(course=currentCourse, student=student).first()
        #If an adapation profile exists for the student, update gamification configuration
        if studentPlayerType:
            playerType = studentPlayerType.playerType
            context_dict['ccparams'].badgesUsed = playerType.badgesUsed
            context_dict['ccparams'].levelingUsed = playerType.levelingUsed
            context_dict['ccparams'].classmatesChallenges = playerType.classmatesChallenges
            context_dict['ccparams'].betVC = playerType.betVC
            context_dict['ccparams'].progressBarUsed= playerType.progressBarUsed
            context_dict['ccparams'].displayStudentStartPageSummary = playerType.displayStudentStartPageSummary
            context_dict['ccparams'].displayAchievementPage = playerType.displayAchievementPage
            context_dict['ccparams'].leaderboardUsed = playerType.leaderboardUsed
            context_dict['ccparams'].virtualCurrencyUsed = playerType.virtualCurrencyUsed
            context_dict['ccparams'].goalsUsed = playerType.goalsUsed
            context_dict['ccparams'].xpDisplayUsed = playerType.xpDisplayUsed
            context_dict['ccparams'].xpLeaderboardUsed = playerType.xpLeaderboardUsed
            
    return context_dict,currentCourse

def studentInstructorInitialContextDict(request):
    
    context_dict, currentCourse = initialContextDict(request)
               
    if 'userID' in request.GET:    
        stud = User.objects.filter(username=request.GET['userID'])
        context_dict["is_teacher"] = True
    else:
        context_dict["is_student"] = True
        stud = request.user

    studentId = Student.objects.filter(user=stud)
    
def checkIfAvatarExist(student):
    avatars = glob.glob('static/images/avatars/*')
    defaultAvatar = '/static/images/avatars/anonymous.png'
    studentAvatarPath = student.avatarImage
    studentAvatarPath = studentAvatarPath[1:]
    if studentAvatarPath in avatars:
        return student.avatarImage
    else:
        student.avatarImage = defaultAvatar #change the students avatar to the default
        student.save()
    
    return defaultAvatar 

def getLevelFromXP(level1_xp, n, leveling_percentage):
    r = 1+(leveling_percentage/100);
    
    if(leveling_percentage==0):
        return level1_xp * n
    
    total = (level1_xp * (1 - pow(r, n ))) / (1-r)
    return total

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")