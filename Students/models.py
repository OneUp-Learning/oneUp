import os

from django.db import models
from django.contrib.auth.models import User
from Instructors.models import Courses, Challenges, Questions, Skills, Activities
from Badges.models import Badges
from Badges.enums import Event, OperandTypes, SystemVariable, Action
from datetime import datetime
from distutils.command.upload import upload
from django.template.defaultfilters import default
from django.conf.global_settings import MEDIA_URL
from oneUp.settings import MEDIA_ROOT, MEDIA_URL, BASE_DIR
from cgi import maxlen

# Create your models here.
 
# Student Information Table used for login purposes.
class Student(models.Model):
    user = models.OneToOneField(User, default=0)
    #User Attributes:
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
    avatarImage= models.CharField(max_length=200, default='')
        
    def __str__(self):              
        #return str(self.studentID)+","+self.name+self.name
        return str(self.user.username)
  
#class for Avatar Images
class UploadedAvatarImage(models.Model):
        avatarImage = models.FileField(max_length=500, upload_to= os.path.join(os.path.abspath(MEDIA_ROOT), 'images/uploadedAvatarImages'))
        avatarImageFileName = models.CharField(max_length=200, default='')

    
# Table listing all the students and the respective courses they are currently registered for   
class StudentRegisteredCourses(models.Model):
    studentID = models.ForeignKey(Student, verbose_name="the related student", db_index=True)
    courseID = models.ForeignKey(Courses, verbose_name="the related course", db_index=True)
    def __str__(self):
        return str(self.studentID) + "," + str(self.courseID)
    
# Students and their corresponding taken challenges information are stored in this table.  
class StudentChallenges(models.Model):
    studentChallengeID = models.AutoField(primary_key=True)
    studentID = models.ForeignKey(Student, verbose_name="the related student", db_index=True)
    courseID = models.ForeignKey(Courses, verbose_name="the related course", db_index=True, default=1)
    challengeID = models.ForeignKey(Challenges, verbose_name="the related challenge", db_index=True)
    startTimestamp = models.DateTimeField()
    endTimestamp = models.DateTimeField()
    testScore = models.DecimalField(decimal_places=2, max_digits=6)  #Actual score earned by the student (We think). Need to test to figure out for certain.
    testTotal = models.DecimalField(decimal_places=2, max_digits=6)  #Total possible score (We think). Need to test to figure out for certain.
    instructorFeedback = models.CharField(max_length=200)
    def __str__(self):              
        return str(self.studentChallengeID) +"," + str(self.studentID) +","+str(self.challengeID)

# This table has each question's score and other information for a student's challenge for all the above table's challenges   
class StudentChallengeQuestions(models.Model):
    studentChallengeQuestionID = models.AutoField(primary_key=True)
    studentChallengeID = models.ForeignKey(StudentChallenges, verbose_name="the related student_challenge", db_index=True)
    questionID = models.ForeignKey(Questions, verbose_name="the related question", db_index=True) 
    questionScore = models.DecimalField(decimal_places=2, max_digits=6)
    questionTotal = models.DecimalField(decimal_places=2, max_digits=6)
    usedHint = models.BooleanField(default=True)
    instructorFeedback = models.CharField(max_length=200)
    def __str__(self):              
        return str(self.studentChallengeQuestionID) +","+str(self.questionID)

# This table has each question's answer that is answered by students for all the above table's questions    
class StudentChallengeAnswers(models.Model):
    studentChallengeQuestionID = models.ForeignKey(StudentChallengeQuestions, verbose_name="the related student_challenge_question", db_index=True)
    studentAnswer = models.CharField(max_length=1000)
    def __str__(self):              
        return str(self.studentChallengeQuestionID) +","+str(self.studentAnswer)

# This table has the matching sorted questions
class MatchShuffledAnswers(models.Model):
    studentChallengeQuestionID = models.ForeignKey(StudentChallengeQuestions, verbose_name="the related student_challenge_question", db_index=True)
    MatchShuffledAnswerText = models.CharField(max_length=1000)
    def __str__(self):              
        return str(self.studentChallengeQuestionID) +","+str(self.MatchShuffledAnswerText)
    
# This table has student-course skills relations information 
class StudentCourseSkills(models.Model):
    studentChallengeQuestionID = models.ForeignKey(StudentChallengeQuestions, verbose_name="the related student_challenge_question", db_index=True)
    skillID = models.ForeignKey(Skills, verbose_name="the related skill", db_index=True)
    skillPoints =  models.IntegerField(default=1)
    def __str__(self):              
        return str(self.studentChallengeQuestionID) +","+str(self.skillID)
    
# This table has student-course skills relations information 
class StudentBadges(models.Model):
    studentBadgeID = models.AutoField(primary_key=True)
    studentID = models.ForeignKey(Student, verbose_name="the student", db_index=True)
    badgeID = models.ForeignKey(Badges, verbose_name="the badge", db_index=True)
    objectID = models.IntegerField(default=-1,verbose_name="index into the appropriate table") #ID of challenge,assignment,etc. associated with a badge
    timestamp = models.DateTimeField(default=datetime.now, blank=True) # AV # Timestamp for badge assignment date
    def __str__(self):              
        return str(self.studentBadgeID) +"," + str(self.studentID) +"," + str(self.badgeID) +"," + str(self.timestamp)
    
class StudentActivities(models.Model):
    studentActivityAssignmentID = models.AutoField(primary_key=True)
    studentID = models.ForeignKey(Student, verbose_name="the related student", db_index=True)
    activityID = models.ForeignKey(Activities, verbose_name="the related activity", db_index=True)
    timestamp = models.DateTimeField()
    activityScore = models.DecimalField(decimal_places=2, max_digits=6)  
    instructorFeedback = models.CharField(max_length=200, default="  ")
    def __str__(self):              
        return str(self.studentActivityAssignmentID) +"," + str(self.studentID) +","+str(self.challengeID)    
    
class StudentEventLog(models.Model):
    student = models.ForeignKey(Student, verbose_name="the student", db_index=True)
    course = models.ForeignKey(Courses, verbose_name="Course in Which event occurred", db_index=True)
    event = models.IntegerField(default=-1,verbose_name="the event which occurred.  Should be a reference to the Event enum", db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="timestamp", db_index=True)
    objectType = models.IntegerField(verbose_name="which type of object is involved, for example, challenge, individual question, or other activity.  Should be a reference to an objectType Enum")
    objectID = models.IntegerField(verbose_name="index into the appropriate tab\
le")
    def __str__(self):
        return 'Event '+str(self.event)+ ' at '+str(self.timestamp)+':'+str(self.event)+' happened to '+str(self.student)+' in course '+str(self.course)
    

# '''
# Student Configuration parameters (goes into studetns.models.py)
# -    Selecting to activate specific game mechanics rules (categories of rules)
# -    Should the system display "How far are they from a particular award"
# '''
class StudentConfigParams(models.Model):
    scpID = models.AutoField(primary_key=True)
    courseID = models.ForeignKey(Courses, verbose_name="the related course", db_index=True)
    studentID = models.ForeignKey(Student, verbose_name="the related student", db_index=True)

    displayBadges = models.BooleanField(default=False)                          ## Student Dashboard display fields
    displayLeaderBoard = models.BooleanField(default=False)
    displayClassSkills = models.BooleanField(default=False) 
    displayClassAverage = models.BooleanField(default=False) 
    displayClassRanking = models.BooleanField(default=False)
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


class Leaderboards(models.Model):
    leaderboardID = models.AutoField(primary_key=True)
    studentID = models.ForeignKey(Student, verbose_name="the related student", db_index=True)
    courseID = models.ForeignKey(Courses, verbose_name = "Course Name", db_index=True)
    def __str__(self):              
        return str(self.leaderboardID)+","+str(self.studentID)                      
           