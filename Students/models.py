import os

from django.db import models
from django.contrib.auth.models import User
from Instructors.models import Courses, Challenges, Questions, Skills, Activities, UploadedFiles
from Badges.models import Badges,BadgesInfo, VirtualCurrencyRuleInfo, VirtualCurrencyCustomRuleInfo
from Badges.enums import Event, OperandTypes, Action
from Badges.systemVariables import SystemVariable
from datetime import datetime
from distutils.command.upload import upload
from django.template.defaultfilters import default
from django.conf.global_settings import MEDIA_URL
from oneUp.settings import MEDIA_ROOT, MEDIA_URL, BASE_DIR
from cgi import maxlen
from Instructors.views.instructorHomeView import instructorHome

# Create your models here.
 
# Student Information Table used for login purposes.
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, default=0)
    #User Attrbutes:
    # username varchar(30)
    # first_name varchar(30)
    # last_name varchar(30)
    # email varchar
    # password hash of password string
    # groups Many-to-Many relationship to Group
    # user_permissions Many-to-Many relationship to Permission
    # is_staff Boolean
    # is_active Boolean
    # is_superuser Boolean
    # last_login DateTime of last log in
    # date_joined DateTime of creation 
    universityID = models.CharField(max_length=100)
    isTestStudent = models.BooleanField(default=False)  # indicates a student to be used by the instructor for testing purposes
    def __str__(self):              
        #return str(self.studentID)+","+self.name+self.name
        if self.user is None:
            return "Unknown student"
        return str(self.user.username)
  
def avatarImageUploadLocation(instance,filename):
    return os.path.join(os.path.join(os.path.abspath(MEDIA_ROOT), 
                                ''),filename)

#class for Avatar Images
class UploadedAvatarImage(models.Model):
        avatarImage = models.FileField(max_length=500,
                                       upload_to= 'images/uploadedAvatarImages')
        avatarImageFileName = models.CharField(max_length=200, default='')
    
# Table listing all the students and the respective courses they are currently registered for   
class StudentRegisteredCourses(models.Model):
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the related student", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="the related course", db_index=True)
    avatarImage= models.CharField(max_length=200, default='')    
    virtualCurrencyAmount = models.IntegerField(default=0)
    def __str__(self):
        return str(self.studentID) + "," + str(self.courseID)
    
# Students and their corresponding taken challenges information are stored in this table.  
class StudentChallenges(models.Model):
    studentChallengeID = models.AutoField(primary_key=True)
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the related student", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="the related course", db_index=True, default=1)
    challengeID = models.ForeignKey(Challenges, on_delete=models.CASCADE, verbose_name="the related challenge", db_index=True)
    startTimestamp = models.DateTimeField()
    endTimestamp = models.DateTimeField()
    testScore = models.DecimalField(decimal_places=2, max_digits=6)  #Actual score earned by the student
    scoreAdjustment = models.DecimalField(decimal_places=2, max_digits=6, default=0) # Individual adjustment to the score 
    adjustmentReason = models.CharField(max_length=1000,default="")
    bonusPointsAwarded = models.DecimalField(decimal_places=2, max_digits=6, default=0)  # Bonus points purchased by the student
    instructorFeedback = models.CharField(max_length=200)
    def __str__(self):              
        return str(self.studentChallengeID) +"," + str(self.studentID) +","+str(self.challengeID)
    def getScore(self):
        return self.testScore + self.scoreAdjustment + self.challengeID.curve    
    def getScoreWithBonus(self):
        return self.testScore + self.scoreAdjustment + self.challengeID.curve + self.bonusPointsAwarded   
        

# This table has each question's score and other information for a student's challenge for all the above table's challenges   
class StudentChallengeQuestions(models.Model):
    studentChallengeQuestionID = models.AutoField(primary_key=True)
    studentChallengeID = models.ForeignKey(StudentChallenges, on_delete=models.CASCADE, verbose_name="the related student_challenge", db_index=True)
    questionID = models.ForeignKey(Questions, on_delete=models.CASCADE, verbose_name="the related question", db_index=True) 
    questionScore = models.DecimalField(decimal_places=2, max_digits=6)
    questionTotal = models.DecimalField(decimal_places=2, max_digits=6)
    usedHint = models.BooleanField(default=True)
    instructorFeedback = models.CharField(max_length=200)
    seed = models.IntegerField(default=0)
    def __str__(self):              
        return str(self.studentChallengeQuestionID) +","+str(self.questionID)

# This table has each question's answer that is answered by students for all the above table's questions    
class StudentChallengeAnswers(models.Model):
    studentChallengeQuestionID = models.ForeignKey(StudentChallengeQuestions, on_delete=models.CASCADE, verbose_name="the related student_challenge_question", db_index=True)
    studentAnswer = models.CharField(max_length=1000)
    def __str__(self):              
        return str(self.studentChallengeQuestionID) +","+str(self.studentAnswer)

# This table has the matching sorted questions
class MatchShuffledAnswers(models.Model):
    studentChallengeQuestionID = models.ForeignKey(StudentChallengeQuestions, on_delete=models.CASCADE, verbose_name="the related student_challenge_question", db_index=True)
    MatchShuffledAnswerText = models.CharField(max_length=1000)
    def __str__(self):              
        return str(self.studentChallengeQuestionID) +","+str(self.MatchShuffledAnswerText)
    
# This table has student-course skills relations information 
class StudentCourseSkills(models.Model):
    studentChallengeQuestionID = models.ForeignKey(StudentChallengeQuestions, on_delete=models.CASCADE, verbose_name="the related student_challenge_question", db_index=True)
    skillID = models.ForeignKey(Skills, on_delete=models.CASCADE, verbose_name="the related skill", db_index=True)
    skillPoints =  models.IntegerField(default=1)
    def __str__(self):              
        return str(self.studentChallengeQuestionID) +","+str(self.skillID)
    
# This table has student-course skills relations information 
class StudentBadges(models.Model):
    studentBadgeID = models.AutoField(primary_key=True)
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the student", db_index=True)
    badgeID = models.ForeignKey(BadgesInfo, on_delete=models.CASCADE, verbose_name="the badge", db_index=True)
    objectID = models.IntegerField(default=-1,verbose_name="index into the appropriate table") #ID of challenge,activity,etc. associated with a badge
    timestamp = models.DateTimeField(default=datetime.now, blank=True) # AV # Timestamp for badge assignment date
    def __str__(self):              
        return str(self.studentBadgeID) +"," + str(self.studentID) +"," + str(self.badgeID) +"," + str(self.timestamp)

class StudentVirtualCurrency(models.Model):
    studentVcID = models.AutoField(primary_key=True)
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the student", db_index=True)
    vcRuleID = models.ForeignKey(VirtualCurrencyCustomRuleInfo, on_delete=models.CASCADE, verbose_name="the virtual currency rule", db_index=True)
    objectID = models.IntegerField(default=-1,verbose_name="index into the appropriate table") #ID of challenge,activity,etc. associated with a virtual currency award
    timestamp = models.DateTimeField(auto_now_add=True) # AV # Timestamp for badge assignment date
    value = models.IntegerField(verbose_name='The amount that was given to the student', default=0)

    def __str__(self):              
        return str(self.studentVcID) +"," + str(self.studentID) +"," + str(self.vcRuleID) +"," + str(self.timestamp)

class StudentActivities(models.Model):
    studentActivityID = models.AutoField(primary_key=True)
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the related student", db_index=True)
    activityID = models.ForeignKey(Activities, on_delete=models.CASCADE, verbose_name="the related activity", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name = "Course Name", db_index=True, default=1)      
    timestamp = models.DateTimeField(default= datetime.now)
    activityScore = models.DecimalField(decimal_places=0, max_digits=6)  
    instructorFeedback = models.CharField(max_length=200, default="No feedback yet ")
    bonusPointsAwarded = models.DecimalField(decimal_places=2, max_digits=6, default=0)  # Bonus points purchased by the student
    graded = models.BooleanField(default=False)
    numOfUploads = models.IntegerField(default = 0)
    comment = models.CharField(max_length=500, default="") #Comment submitted by student
    submissionTimestamp = models.DateTimeField(default= datetime.now)
    def __str__(self):              
        return str(self.studentActivityID) +"," + str(self.studentID) 
    def getScoreWithBonus(self):
        return self.activityScore + self.bonusPointsAwarded

class StudentAttendance(models.Model):
    studentAttendanceID = models.AutoField(primary_key=True)
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the related student", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name = "Course Name", db_index=True, default=1)      
    timestamp = models.DateTimeField(default= datetime.now)
    isPresent = models.BooleanField(default=False)
    def __str__(self):              
        return str(self.studentAttendanceID) +"," + str(self.studentID)    
    
def fileUploadPath(instance,filename):
    return os.path.join(os.path.join(os.path.abspath(MEDIA_ROOT), 'studentActivities'),filename)


#Object to hold student files and where they are located at 
class StudentFile(models.Model):
    studentFileID = models.AutoField(primary_key=True)
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the related student", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="the related course", db_index=True)
    activity = models.ForeignKey(StudentActivities, on_delete=models.CASCADE, verbose_name= 'the related activity')
    timestamp = models.DateTimeField(default=datetime.now)
    file = models.FileField(max_length=500,upload_to= fileUploadPath)
    fileName = models.CharField(max_length=200, default='')
    latest = models.BooleanField(default = True)
    
    
    def delete(self):
        self.file.delete()
        super(StudentFile, self).delete()
        
    def removeFile(self):
        self.file.delete()

class StudentEventLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="the student", db_index=True)
    course = models.ForeignKey(Courses, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Course in Which event occurred", db_index=True)
    event = models.IntegerField(default=-1,verbose_name="the event which occurred.  Should be a reference to the Event enum", db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="timestamp", db_index=True)
    objectType = models.IntegerField(verbose_name="which type of object is involved, for example, challenge, individual question, or other activity.  Should be a reference to an objectType Enum")
    objectID = models.IntegerField(verbose_name="index into the appropriate table")
    
    def __str__(self):
        return 'Event '+str(self.event)+ ' at '+str(self.timestamp)+':'+str(self.event)+' happened to '+str(self.student)+' in course '+str(self.course)
    
class StudentVirtualCurrencyTransactions(models.Model):
    transactionID = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the student", db_index=True)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="Course in Which event occurred", db_index=True)
    studentEvent = models.ForeignKey(StudentEventLog, on_delete=models.CASCADE, verbose_name="the Student Event Log", db_index=True)
    objectType = models.IntegerField(verbose_name="which type of object is involved, for example, challenge, individual question, or other activity.  Should be a reference to an objectType Enum")
    objectID = models.IntegerField(verbose_name="index into the appropriate table")
    status = models.CharField(max_length=200, default='Requested')
    noteForStudent = models.CharField(max_length=600)
    instructorNote = models.CharField(max_length=600)
    
    def __str__(self):
        return 'ID: '+ str(self.transactionID)+', Student: '+str(self.student)+ ' Course: '+str(self.course)+' Event: '+str(self.studentEvent)+'Object Type: '+str(self.objectType)+' ObjectID: '+str(self.objectID)+' Status: '+str(self.status)+' StudentNote: '+str(self.noteForStudent)+' InstructorNote: '+str(self.instructorNote)
    


# '''
# Student Configuration parameters (goes into studetns.models.py)
# -    Selecting to activate specific game mechanics rules (categories of rules)
# -    Should the system display "How far are they from a particular award"
# '''
    
class StudentConfigParams(models.Model):
    scpID = models.AutoField(primary_key=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="the related course", db_index=True)
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the related student", db_index=True)

    displayBadges = models.BooleanField(default=True)                          ## Student Dashboard display fields
    displayLeaderBoard = models.BooleanField(default=True)
    displayClassSkills = models.BooleanField(default=True) 
    displayClassAverage = models.BooleanField(default=True) 
    displayClassRanking = models.BooleanField(default=True)
    courseBucks = models.IntegerField(default=0)
    
    def __str__(self):
        return str(self.scpID)  +","
        +str(self.courseID) +","
        +str(self.studentID) +","
        +str(self.displayBadges) +","                           
        +str(self.displayLeaderBoard) +","                      
        +str(self.displayClassSkills) +","                      
        +str(self.displayClassAverage) +","                     
        +str(self.displayClassRanking)    


class StudentLeaderboardHistory(models.Model):
    id = models.AutoField(primary_key=True)
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the related student", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name = "Course Name", db_index=True)
    leaderboardPosition = models.IntegerField(default=0) # Position is ranked starting from 1.
    startTimestamp = models.DateTimeField(auto_now_add=True, verbose_name="Start Timestamp", db_index=True)
    endTimestamp = models.DateTimeField(null=True, blank=True, verbose_name="End Timestamp", db_index=True)

    def __str__(self):              
        return str(self.id)+", "+str(self.studentID)+", Position: "+str(self.leaderboardPosition)+", Start Timestamp: "+str(self.startTimestamp)+", End Timestamp: "+str(self.endTimestamp)                             
           
# Duel challenge related tables
class DuelChallenges(models.Model): 
    duelChallengeID = models.AutoField(primary_key=True)
    duelChallengeName = models.CharField(max_length=100)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name = "Course Name", db_index=True)
    challengeID = models.ForeignKey(Challenges, on_delete=models.CASCADE, verbose_name="the related challenge", db_index=True)
    isBetting = models.BooleanField(default=False) # Indicates betting with virtual currency
    vcBet = models.IntegerField(default=0) # the amount of virtual currency being bet
    challenger = models.ForeignKey(Student, related_name='challenger',on_delete=models.CASCADE, verbose_name="the related student", db_index=True)
    challengee = models.ForeignKey(Student, related_name='challengee',on_delete=models.CASCADE, verbose_name="the related student", db_index=True)
    sendTime = models.DateTimeField(auto_now_add=True, verbose_name="Send Timestamp", db_index=True)
    acceptTime = models.DateTimeField(auto_now_add=True, verbose_name="Accept Timestamp", db_index=True)
    startTime = models.IntegerField(default=1440) # time in minutes, Default 24 hours
    timeLimit = models.IntegerField(default=120)  # time in minutes, Default 1 hour
    customMessage = models.CharField(max_length=600, default='')
    status = models.IntegerField(default=1) # Indicates the status of the challenge 0=canceled ,1=pending, 2=accepted
    hasStarted = models.BooleanField(default=False) # Indicates whether the challenge has begun
    hasEnded = models.BooleanField(default=False) # Indicates whether the challenge has ended
     
# This table considers a tie as a win, it stores winners and those in ties
class Winners(models.Model):
    DuelChallengeID = models.ForeignKey(DuelChallenges, on_delete=models.CASCADE, verbose_name="the related Duel", db_index=True)
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the related student", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="the related course", db_index=True)
    
    