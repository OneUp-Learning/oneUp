import os
from cgi import maxlen
from datetime import datetime

from django.conf.global_settings import MEDIA_URL
from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import default
from django.utils.timezone import now

from Badges.enums import Action, Event, OperandTypes
from Badges.models import (Badges, BadgesInfo, LeaderboardsConfig,
                           ProgressiveUnlocking, Rules,
                           VirtualCurrencyCustomRuleInfo,
                           VirtualCurrencyRuleInfo, PlayerType)
from Badges.systemVariables import SystemVariable
from Instructors.models import (Activities, Challenges, ChallengesQuestions,
                                Courses, FlashCards, Questions, Skills,
                                UploadedFiles)
from Instructors.views.instructorHomeView import instructorHome
from oneUp.settings import BASE_DIR, MEDIA_ROOT, MEDIA_URL


def custom_now():
    return now().replace(microsecond=0)

 
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
    displayDarkMode = models.BooleanField(default=False) # Enables dark theme for the student across courses
    def __str__(self):              
        #return str(self.studentID)+","+self.name+self.name
        if self.user is None:
            return "Unknown student"
        return str(self.user.username)
  
def avatarImageUploadLocation(instance,filename):
    return os.path.join(os.path.join(os.path.abspath(MEDIA_ROOT), ''),filename)

#class for Avatar Images
class UploadedAvatarImage(models.Model):
    avatarImage = models.FileField(max_length=500, upload_to= 'images/uploadedAvatarImages')
    avatarImageFileName = models.CharField(max_length=200, default='')
    
# Table listing all the students and the respective courses they are currently registered for   
class StudentRegisteredCourses(models.Model):
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the related student", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="the related course", db_index=True)
   
    avatarImage= models.CharField(max_length=200, default='')
    # VirtualCurrenyAmount is essentially a cache for this value
    # The actual official total is dervied from transactions stored
    # in the database in the models StudentVirtualCurrencyTransactions
    # and StudentVirtualCurrency
    # It is calculated using recalculate_student_virtual_currency_total
    # from Badges/event.py/
    virtualCurrencyAmount = models.IntegerField(default=0)
    donationAmount = models.IntegerField(default=0)
    attendanceStreakStartDate = models.DateTimeField(default=custom_now)
    # This is a cache of the XP amount, used because calculating it live
    # all the time is too slow.
    # Recalculate this using the refresh_xp function.
    xp = models.DecimalField(decimal_places=2, max_digits=100, default=0)
    level = models.IntegerField(default=0)
    def __str__(self):
        return str(self.studentID) + "," + str(self.courseID)
    
# Students and their corresponding taken challenges information are stored in this table.  
class StudentChallenges(models.Model):
    studentChallengeID = models.AutoField(primary_key=True)
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the related student", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="the related course", db_index=True, default=1)
    challengeID = models.ForeignKey(Challenges, on_delete=models.CASCADE, verbose_name="the related challenge", db_index=True)
    startTimestamp = models.DateTimeField(default=custom_now)
    endTimestamp = models.DateTimeField(default=custom_now)
    testScore = models.DecimalField(decimal_places=2, max_digits=6)  #Actual score earned by the student
    scoreAdjustment = models.DecimalField(decimal_places=2, max_digits=6, default=0) # Individual adjustment to the score 
    adjustmentReason = models.CharField(max_length=1000,default="")
    bonusPointsAwarded = models.DecimalField(decimal_places=2, max_digits=6, default=0)  # Bonus points purchased by the student
    instructorFeedback = models.CharField(max_length=200)
    def __str__(self):              
        return str(self.studentChallengeID) +"," + str(self.studentID) +","+str(self.challengeID)
    def getScore(self):
        if self.testScore == 0:
            return 0
        return self.testScore + self.scoreAdjustment + self.challengeID.curve    
    def getScoreWithBonus(self):
        if self.testScore == 0:
            return self.scoreAdjustment+self.bonusPointsAwarded
        return self.testScore + self.scoreAdjustment + self.challengeID.curve + self.bonusPointsAwarded   
        

# This table has each question's score and other information for a student's challenge for all the above table's challenges   
class StudentChallengeQuestions(models.Model):
    studentChallengeQuestionID = models.AutoField(primary_key=True)
    studentChallengeID = models.ForeignKey(StudentChallenges, on_delete=models.CASCADE, verbose_name="the related student_challenge", db_index=True)
    questionID = models.ForeignKey(Questions, on_delete=models.CASCADE, verbose_name="the related question", db_index=True) 
    challengeQuestionID = models.ForeignKey(ChallengesQuestions, on_delete=models.CASCADE, verbose_name="the related challenge_question", db_index=True) 
    questionScore = models.DecimalField(decimal_places=2, max_digits=6)
    questionTotal = models.DecimalField(decimal_places=2, max_digits=6)
    usedHint = models.BooleanField(default=False)
    instructorFeedback = models.CharField(max_length=200)
    seed = models.IntegerField(default=0)
    def __str__(self):              
        return str(self.studentChallengeQuestionID) +","+str(self.questionID)

# This table has each question's answer that is answered by students for all the above table's questions    
class StudentChallengeAnswers(models.Model):
    studentChallengeQuestionID = models.ForeignKey(StudentChallengeQuestions, on_delete=models.CASCADE, verbose_name="the related student_challenge_question", db_index=True)
    studentAnswer = models.CharField(max_length=10000)
    def __str__(self):              
        return str(self.studentChallengeQuestionID) +","+str(self.studentAnswer)

# This table stores the hints per question for a student
class StudentAnswerHints(models.Model):
    studentAnswerHintsID = models.AutoField(primary_key=True)
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the related student", db_index=True)
    challengeQuestionID =  models.IntegerField(default=0) #we need to hold it temporarily, we update studentChallengeQuestionID aftwards with the instance
    usedBasicHint = models.BooleanField(default=False)
    usedStrongHint = models.BooleanField(default=False)
    studentChallengeQuestionID = models.ForeignKey(StudentChallengeQuestions, on_delete=models.CASCADE, verbose_name="the related student_challenge_question hint",null=True)
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
    timestamp = models.DateTimeField(default=custom_now, blank=True) # AV # Timestamp for badge assignment date
    def __str__(self):              
        return str(self.studentBadgeID) +"," + str(self.studentID) +"," + str(self.badgeID) +"," + str(self.timestamp)

class StudentVirtualCurrency(models.Model):
    studentVcID = models.AutoField(primary_key=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="the course", db_index=True, default=1)
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the student", db_index=True)
    objectID = models.IntegerField(default=-1,verbose_name="index into the appropriate table") #ID of challenge,activity,etc. associated with a virtual currency award
    timestamp = models.DateTimeField(default=custom_now) # AV # Timestamp for badge assignment date
    value = models.IntegerField(verbose_name='The amount that was given to the student', default=0)
    vcName = models.CharField(max_length=300, null=True, blank=True)  
    vcDescription = models.CharField(max_length=4000, null=True, blank=True)
    def __str__(self):              
        return str(self.studentVcID) +"," + str(self.studentID) +"," + str(self.timestamp)
class StudentVirtualCurrencyRuleBased(StudentVirtualCurrency):
    vcRuleID = models.ForeignKey(VirtualCurrencyCustomRuleInfo, related_name="vcrule", on_delete=models.SET_NULL, verbose_name="the virtual currency rule", db_index=True, null=True, blank=True)

    def __str__(self):              
        return str(self.studentVcID) +"," + str(self.studentID) +"," + str(self.timestamp)
    
class StudentGoalSetting(models.Model):
    studentGoalID = models.AutoField(primary_key=True)
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the student", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="the course", db_index=True, default=1)
    ruleID = models.ForeignKey(Rules, on_delete=models.SET_NULL, verbose_name="the goal rule", null=True, db_index=True)
    goalVariable = models.IntegerField(default=0,verbose_name="The goal variable selected by the student. Should be a system variable index", db_index=True)
    timestamp = models.DateTimeField(default=custom_now) # AV # Timestamp for date the goal was created
    targetExact = models.BooleanField(verbose_name='Indicates whether the targetedNumber should be used as a exact match or should be used as amount to gain each week', default=True)
    targetedNumber = models.FloatField(verbose_name='A number related to the goal.', default=0)  #This can be the number of warm-up challenges to be taken or the number of days in a streak
    progressToGoal = models.FloatField(verbose_name='A percentage of the students progress towards the goal.', default=0)
    recurringGoal = models.BooleanField(verbose_name='A boolean value to indicate whether goal has recurrence.', default=True)
    completed = models.BooleanField(verbose_name='Indicates whether the goal is completed and no longer has a rule associated with it', default=False)

    def __str__(self):              
        return str(self.studentGoalID) +"," + str(self.studentID) +"," + str(self.timestamp)

class StudentActivities(models.Model):
    studentActivityID = models.AutoField(primary_key=True)
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the related student", db_index=True)
    activityID = models.ForeignKey(Activities, on_delete=models.CASCADE, verbose_name="the related activity", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name = "Course Name", db_index=True, default=1)     

    timestamp = models.DateTimeField(default= custom_now, verbose_name="Grading Timestamp") # represents when the activity was graded (if it has been)
    hasTimestamp = models.BooleanField(default=False) # Flags used to determine if the timestamp should be used or not

    submissionTimestamp = models.DateTimeField(default= custom_now, verbose_name="Latest submission timestamp") # represents when the activity was submitted
    submitted = models.BooleanField(default=False) # Flags used to determine if the student has submitted or not

    activityScore = models.DecimalField(decimal_places=0, max_digits=6)  
    instructorFeedback = models.CharField(max_length=20000, default="")
    bonusPointsAwarded = models.DecimalField(decimal_places=2, max_digits=6, default=0)  # Bonus points purchased by the student
    graded = models.BooleanField(default=False)
    numOfUploads = models.IntegerField(default = 0)
    
    richTextSubmission = models.CharField(max_length=20000, null=True, blank=True)
    comment = models.CharField(max_length=500, default="") #Comment submitted by student
    def __str__(self):              
        return str(self.studentActivityID) +"," + str(self.studentID) 
    def getScoreWithBonus(self):
        return self.activityScore + self.bonusPointsAwarded

class StudentAttendance(models.Model):
    studentAttendanceID = models.AutoField(primary_key=True)
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the related student", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name = "Course Name", db_index=True, default=1)      
    timestamp = models.DateTimeField(default= custom_now)
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
    timestamp = models.DateTimeField(default=custom_now)
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
    timestamp = models.DateTimeField(default=custom_now, verbose_name="timestamp", db_index=True)
    objectType = models.IntegerField(verbose_name="which type of object is involved, for example, challenge, individual question, or other activity.  Should be a reference to an objectType Enum")
    objectID = models.IntegerField(verbose_name="index into the appropriate table")
    
    def __str__(self):
        if self.event in Event.events:
            eventName = Event.events[self.event]["name"]
        else:
            eventName = "Unknown Event"
        return 'Event '+eventName+'('+str(self.event)+') at '+str(self.timestamp)+':'+str(self.event)+' happened to '+str(self.student)+' in course '+str(self.course) + ' obj id ' + str(self.objectID)
    
class StudentVirtualCurrencyTransactions(models.Model):
    transactionID = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the student", db_index=True)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="Course in Which event occurred", db_index=True)
    studentEvent = models.ForeignKey(StudentEventLog, on_delete=models.CASCADE, verbose_name="the Student Event Log", db_index=True)
    objectType = models.IntegerField(verbose_name="which type of object is involved, for example, challenge, individual question, or other activity.  Should be a reference to an objectType Enum")
    objectID = models.IntegerField(verbose_name="index into the appropriate table")
    name = models.CharField(default="", max_length=300, verbose_name="The name of the transaction (usually the vcRuleName a rule") 
    description = models.CharField(default="", max_length=4000, verbose_name="The description of the transaction (usually the vcDescription a rule")
    amount = models.IntegerField(default=0, verbose_name="The amount of the transaction (usually the vcAmount a rule")
    status = models.CharField(max_length=200, default='Requested')
    noteForStudent = models.CharField(max_length=600)
    instructorNote = models.CharField(max_length=600)
    transactionReason = models.CharField(max_length=600, default="") # Reason for making the transaction
    timestamp = models.DateTimeField(default=custom_now, verbose_name="timestamp", db_index=True, blank=True, null=True)

    
    def __str__(self):
        return 'ID: '+ str(self.transactionID)+', Student: '+str(self.student)+ ' Course: '+str(self.course)+' Event: '+str(self.studentEvent)+'Object Type: '+str(self.objectType)+' ObjectID: '+str(self.objectID)+' Status: '+str(self.status)+' StudentNote: '+str(self.noteForStudent)+' InstructorNote: '+str(self.instructorNote) + ' transactionReason'+self.transactionReason
    


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
    participateInDuel = models.BooleanField(default=True)
    participateInCallout = models.BooleanField(default=True)
    courseBucks = models.IntegerField(default=0)
    displayGoal = models.BooleanField(default=True)
    def __str__(self):
        return str(self.scpID)  +","+str(self.courseID) +","+str(self.studentID) +",displayBadges:"+str(self.displayBadges) +",displayLeaderboard:"+str(self.displayLeaderBoard) +",displayClassSkills"+str(self.displayClassSkills) +",displayClassAverage:"+str(self.displayClassAverage) +",displayClassRanking:"+str(self.displayClassRanking) +",displayGoal:"+str(self.displayGoal)+",participateInDuel:"+str(self.participateInDuel)+",courseBucks:"+str(self.courseBucks)   

class PeriodicallyUpdatedleaderboards(models.Model):
    periodicLeaderboardID = models.AutoField(primary_key=True)
    leaderboardID = models.ForeignKey(LeaderboardsConfig, on_delete=models.CASCADE, verbose_name="the related leaderboard configuration object", db_index=True)
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the related student", db_index=True)
    studentPoints = models.IntegerField(default=0)
    studentPosition = models.IntegerField(default=0)
      
    def __str__(self):              
        return str(self.periodicLeaderboardID)+", LeaderboardID: "+str(self.leaderboardID) + ", StudentID: "+str(self.studentID)+", Points: "+str(self.studentPoints)+", Position: "+str(self.studentPosition)
    

class StudentLeaderboardHistory(models.Model):
    id = models.AutoField(primary_key=True)
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the related student", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name = "Course Name", db_index=True)
    leaderboardPosition = models.IntegerField(default=0) # Position is ranked starting from 1.
    startTimestamp = models.DateTimeField(default=custom_now, verbose_name="Start Timestamp", db_index=True)
    endTimestamp = models.DateTimeField(default=custom_now, null=True, blank=True, verbose_name="End Timestamp", db_index=True)

    def __str__(self):              
        return str(self.id)+", "+str(self.studentID)+", Position: "+str(self.leaderboardPosition)+", Start Timestamp: "+str(self.startTimestamp)+", End Timestamp: "+str(self.endTimestamp)                             
           
class DuelChallenges(models.Model): 
    duelChallengeID = models.AutoField(primary_key=True)
    duelChallengeName = models.CharField(max_length=100)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name = "Course Name", db_index=True)
    challengeID = models.ForeignKey(Challenges, on_delete=models.CASCADE, verbose_name="the related challenge", db_index=True)
    isBetting = models.BooleanField(default=False) # Indicates betting with virtual currency
    vcBet = models.IntegerField(default=0) # the amount of virtual currency being bet
    challenger = models.ForeignKey(Student, related_name='challenger',on_delete=models.CASCADE, verbose_name="the related student", db_index=True)
    challengee = models.ForeignKey(Student, related_name='challengee',on_delete=models.CASCADE, verbose_name="the related student", db_index=True)
    sendTime = models.DateTimeField(default=custom_now, verbose_name="Send Timestamp", db_index=True)
    acceptTime = models.DateTimeField(default=custom_now, verbose_name="Accept Timestamp", db_index=True)
    startTime = models.IntegerField(default=1440) # time in minutes, Default 24 hours
    timeLimit = models.IntegerField(default=120)  # time in minutes, Default 1 hour
    customMessage = models.CharField(max_length=6000, default='')
    status = models.IntegerField(default=1) # Indicates the status of the challenge 0=canceled ,1=pending, 2=accepted
    hasStarted = models.BooleanField(default=False) # Indicates whether the challenge has begun
    hasEnded = models.BooleanField(default=False) # Indicates whether the challenge has ended
    evaluator = models.IntegerField(default=0) # The student who is going to evaluate the duel 0=unknown, 1=chanllenger, 2=challengee
    hasExpired = models.BooleanField(default=False) # Indicates whether the challenge has expired

    def __str__(self):
        return "duelchallengeID: "+str(self.duelChallengeID)+ ", duelchallengeName: "+ str(self.duelChallengeName)+", courseID: "+str(self.courseID)+", challengeID: "+str(self.challengeID)+\
            ", isBetting: "+str(self.isBetting)+", vcBet: "+str(self.vcBet)+", challenger: "+str(self.challenger)+", challengee: "+str(self.challengee)+", sendTime: "+str(self.sendTime)+\
            ", acceptTime: "+str(self.acceptTime)+", startTime:"+str(self.startTime)+", timeLimit: "+str(self.timeLimit)+", customMessage: "+str(self.customMessage)+\
            " status: "+str(self.status)+" hasStarted: "+str(self.hasStarted)+" hasEnded: "+str(self.hasEnded)+" hasExpired: "+str(self.hasExpired)
     
# This table considers a tie as a win, it stores winners and those in ties
class Winners(models.Model):
    DuelChallengeID = models.ForeignKey(DuelChallenges, on_delete=models.CASCADE, verbose_name="the related Duel", db_index=True)
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the related student", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="the related course", db_index=True)

    def __str__(self):
        return "duelChallengeID: "+str(self.DuelChallengeID)+", studentID: "+str(self.studentID)+", courseID: "+str(self.courseID)

class Callouts(models.Model): 
    calloutID = models.AutoField(primary_key=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name = "Course Name", db_index=True)
    challengeID = models.ForeignKey(Challenges, on_delete=models.CASCADE, verbose_name="the related challenge", db_index=True)
    sender = models.ForeignKey(Student, related_name="sender" ,on_delete=models.CASCADE, verbose_name="the related student", db_index=True)
    sendTime = models.DateTimeField(default=custom_now, verbose_name="Send Timestamp", db_index=True)
    endTime = models.DateTimeField(default=custom_now, verbose_name="End Time", db_index=True)
    customMessage = models.CharField(max_length=6000, default='')
    hasEnded = models.BooleanField(default=False) # Indicates whether the callout  has ended
    isIndividual = models.BooleanField() # Indicates whether the callout  is individual if it is true or whole class if it is not true

    def __str__(self):
        return "calloutID: "+str(self.calloutID)+", courseID: "+str(self.courseID)+", challengeID: "+str(self.challengeID)+", sender: "+str(self.sender)+", sendTime: "+str(self.sendTime)+", endTime: "+str(self.endTime)+", customMessage: "+str(self.customMessage)+", hasEnded: "+str(self.hasEnded)+",  isIndividual: "+str(self.isIndividual)

class CalloutParticipants(models.Model):
    calloutID = models.ForeignKey(Callouts, on_delete=models.CASCADE, verbose_name="the related Callout", db_index=True)
    participantID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the related student", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="the related course", db_index=True)
    hasSubmitted = models.BooleanField(default=False) # Indicates whether the callout  has submitted by student
    hasWon = models.BooleanField(default=False) # Indicates whether the participant has won 

    def __str__(self):
        return "calloutID: "+str(self.calloutID)+", participantID: "+str(self.participantID)+", courseID: "+str(self.courseID)+", hasSubmitted: "+str(self.hasSubmitted)+", hasWon: "+str(self.hasWon)

class CalloutStats(models.Model):
    calloutID = models.ForeignKey(Callouts, on_delete=models.CASCADE, verbose_name="the related Callout", db_index=True)
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the related student", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="the related course", db_index=True)
    studentChallenge =  models.ForeignKey(StudentChallenges, on_delete=models.CASCADE, verbose_name="the related student challenge", db_index=True)
    calloutVC = models.IntegerField()
    submitTime = models.DateTimeField(default=custom_now, verbose_name="Send Timestamp", db_index=True) # record submit time if there is any submit

    def __str__(self):
        return "calloutID: "+str(self.calloutID)+", studentID: "+str(self.studentID)+", courseID: "+str(self.courseID)+", student challenge: "+str(self.studentChallenge) +", callout vc: "+str(self.calloutID) + ", submit time "+ str(self.submitTime)

class StudentStreaks(models.Model):
    studentStreakID = models.AutoField(primary_key=True)
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the related student", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="the related course", db_index=True)
    streakStartDate = models.DateTimeField(default=custom_now, null=True, blank=True, verbose_name="The date the streak reset on")
    streakType = models.IntegerField(default=0)
    objectID = models.IntegerField(default=0) #0 badge 1 vc
    currentStudentStreakLength = models.IntegerField(default=0)
    
    
class StudentProgressiveUnlocking(models.Model):
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the student", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name = "Course Name", db_index=True)
    pUnlockingRuleID = models.ForeignKey(ProgressiveUnlocking, on_delete=models.CASCADE, verbose_name="the progressive unlocking rule", db_index=True)
    objectID = models.IntegerField(default=-1,verbose_name="index into the appropriate table") #ID of challenge,activity,etc. associated with a unlocking rule
    objectType = models.IntegerField(verbose_name="which type of object is involved, for example, challenge, individual question, or other activity.  Should be a reference to an objectType Enum", db_index=True,default=1301) # Defaulted to Challenges
    timestamp = models.DateTimeField(default=custom_now) # AV # Timestamp for badge assignment date
    isFullfilled = models.BooleanField(verbose_name='Did the student fullfill the unlocking rule', default=False)
    
    def __str__(self):
        return "student:"+str(self.studentID)+" course:"+str(self.courseID)+" rule:"+str(self.pUnlockingRuleID)+" obj:"+str(self.objectID)+","+str(self.objectType)+" done:"+str(self.isFullfilled)

class StudentActions(models.Model):
    ''' Ultility model which will be used for thesis work. Collects infromation about each student
        and what actions they have done (warmups/serious challenge attempts or duels/callouts) over 
        some X time.
    '''
    studentActionsID = models.AutoField(primary_key=True)
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the student", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name = "Course Name", db_index=True)
    json_data = models.TextField(blank=True, default='{}', verbose_name='Student JSON Results',
            help_text='JSON encoded table of student results')
    timestamp = models.DateTimeField(auto_now=True, verbose_name='Created Timestamp')
    def __str__(self):
        return "{} : {} : {} : {}".format(self.studentActionsID, self.courseID, self.studentID, self.timestamp)

class StudentActionsLoop(models.Model):
    ''' Ultility model which will be used for thesis work. Collects infromation about each student
        and what actions they have done (warmups/serious challenge attempts or duels/callouts) over 
        some X time.
    '''
    studentActionsLoopID = models.AutoField(primary_key=True)
    studentActionsID = models.ForeignKey(StudentActions, on_delete=models.CASCADE, verbose_name="the overall loop", db_index=True)
    # Actions
    warmups_attempted = models.IntegerField(default=0,verbose_name="# of Warmups Attempted")
    serious_attempted = models.IntegerField(default=0,verbose_name="# of Serious Challenges Attempted")
    duels_sent = models.IntegerField(default=0,verbose_name="# of Duels Sent")
    duels_accepted = models.IntegerField(default=0,verbose_name="# of Duels Accepted")
    callouts_sent = models.IntegerField(default=0,verbose_name="# of Callouts Accpeted")
    callouts_participated = models.IntegerField(default=0,verbose_name="# of Callouts Participated")

    # Postivie Feedback
    high_score_challenges = models.IntegerField(default=0, verbose_name="# of High Score Challenges")
    vc_earned = models.IntegerField(default=0, verbose_name="# of VC Earned")
    badges_earned = models.IntegerField(default=0, verbose_name="# of Badges Earned")
    on_leaderboard = models.BooleanField(default=False, verbose_name="Appeared on Leaderboard")
    duels_won = models.IntegerField(default=0, verbose_name="# of Duels Won")
    callouts_won = models.IntegerField(default=0, verbose_name="# of Callouts Won")

    # Negative Feedback
    low_score_challenges = models.IntegerField(default=0, verbose_name="# of Low Score Challenges")
    duels_lost = models.IntegerField(default=0, verbose_name="# of Duels Lost")
    callouts_lost = models.IntegerField(default=0, verbose_name="# of Callouts Lost")

    timestamp = models.DateTimeField(auto_now=True, verbose_name='Created Timestamp')
    def __str__(self):
        return "{} : {} : {}".format(self.studentActionsLoopID, self.studentActionsID, self.timestamp)

class studentFlashCards(models.Model):
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the student", db_index=True)
    flashID = models.ForeignKey(FlashCards,on_delete=models.CASCADE, verbose_name="the flash card",db_index=True)
    studyDate = models.DateTimeField(default=custom_now, verbose_name="the ideal date the flash card should reappear", db_index=True)
    cardBin = models.IntegerField(default=0, verbose_name="priority containers for flash cards", db_index=True)
    timesSeen = models.IntegerField(default=0, verbose_name="times the student has seen the card")
    timesCorrect = models.IntegerField(default=0, verbose_name="times the student has correctly answered the card")

    def __str__(self):
        return "{} : {} : {} : {} : {} : {}".format(self.studentID, self.flashID, self.studyDate, self.cardBin, self.timesSeen, self.timesCorrect)



class Teams(models.Model):
    teamID = models.AutoField(primary_key=True)
    courseID = models.ForeignKey(Courses,on_delete=models.CASCADE, verbose_name="the course",db_index=True)
    #team leader designation meant to allow for editing teams settings/interacting with the server during challenges/activities
    teamLeader = models.ForeignKey(Student,on_delete=models.CASCADE, blank=True, null=True, verbose_name="the team's leader",db_index=True)
    teamName = models.CharField(max_length=100, default='')
    avatarImage= models.CharField(max_length=200, default='')
    #Allows for multiple team sets throughout a course, set to false when creating a new group of teams
    activeTeam = models.BooleanField(default=True, verbose_name = 'Indicates whether or not team is in current set of active teams')

    def __str__(self):
        return "{} : {} : {} : {} : {} : {}".format(self.teamID, self.courseID, self.teamLeader, self.teamName, self.avatarImage, self.activeTeam)

class TeamStudents(models.Model):
    teamID = models.ForeignKey(Teams, on_delete=models.CASCADE, verbose_name="the team", db_index=True)
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the student", db_index=True)
    #Allows for multiple team sets throughout a course, set to false when creating a new group of teams
    activeMember = models.BooleanField(default = True, verbose_name = 'Indicates whether student is currently an active member of team')
    #indicates how the student was enrolled in the team: S = self-enrolled, I = Individually by instructor, A = auto-assigned by instructor
    modeOfEnrollment = models.CharField(max_length=1, default = '')
    def __str__(self):
        return "{} : {} : {} : {}".format(self.teamID, self.studentID, self.activeMember, self.modeOfEnrollment)
class TeamChallenges(models.Model):
    teamChallengeID = models.AutoField(primary_key=True)
    teamID = models.ForeignKey(Teams, on_delete=models.CASCADE, verbose_name="the related team", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="the related course", db_index=True, default=1)
    challengeID = models.ForeignKey(Challenges, on_delete=models.CASCADE, verbose_name="the related challenge", db_index=True)
    startTimestamp = models.DateTimeField(default=custom_now)
    endTimestamp = models.DateTimeField(default=custom_now)
    testScore = models.DecimalField(decimal_places=2, max_digits=6)  #Actual score earned by the team
    scoreAdjustment = models.DecimalField(decimal_places=2, max_digits=6, default=0) # Individual adjustment to the score 
    adjustmentReason = models.CharField(max_length=1000,default="")
    instructorFeedback = models.CharField(max_length=200)
    
    def __str__(self):
        return "{} : {} : {} : {}".format(self.teamChallengeID, self.teamID, self.courseID, self.challengeID)
    
    def getScore(self):
        if self.testScore == 0:
            return 0
        return self.testScore + self.scoreAdjustment + self.challengeID.curve   

# This table has each question's score and other information for a team's challenge for all the above table's challenges   
class TeamChallengeQuestions(models.Model):
    teamChallengeQuestionID = models.AutoField(primary_key=True)
    teamChallengeID = models.ForeignKey(TeamChallenges, on_delete=models.CASCADE, verbose_name="the related team challenge", db_index=True)
    questionID = models.ForeignKey(Questions, on_delete=models.CASCADE, verbose_name="the related question", db_index=True) 
    challengeQuestionID = models.ForeignKey(ChallengesQuestions, on_delete=models.CASCADE, verbose_name="the related challenge question", db_index=True) 
    questionScore = models.DecimalField(decimal_places=2, max_digits=6)
    questionTotal = models.DecimalField(decimal_places=2, max_digits=6)
    instructorFeedback = models.CharField(max_length=200)
    seed = models.IntegerField(default=0)
   
    def __str__(self):
        return "{} : {} : {} : {}".format(self.teamChallengeQuestionID, self.teamChallengeID, self.questionID, self.challengeQuestionID)

# This table has each question's answer that is answered by teams for all the above table's questions    

class TeamChallengeAnswers(models.Model):
    teamChallengeQuestionID = models.ForeignKey(TeamChallengeQuestions, on_delete=models.CASCADE, verbose_name="the related team_challenge_question", db_index=True)
    teamAnswer = models.CharField(max_length=10000)
    def __str__(self):              
        return str(self.teamChallengeQuestionID) +","+str(self.teamAnswer)

class TeamActivities(models.Model):
    teamActivityID = models.AutoField(primary_key=True)
    teamID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the related team", db_index=True)
    activityID = models.ForeignKey(Activities, on_delete=models.CASCADE, verbose_name="the related activity", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name = "Course Name", db_index=True, default=1)     

    timestamp = models.DateTimeField(default= custom_now, verbose_name="Grading Timestamp") # represents when the team activity was graded (if it has been)
    hasTimestamp = models.BooleanField(default=False) # Flags used to determine if the timestamp should be used or not

    submissionTimestamp = models.DateTimeField(default= custom_now, verbose_name="Latest submission timestamp") # represents when the team activity was submitted
    submitted = models.BooleanField(default=False) # Flags used to determine if the student has submitted or not
    activityScore = models.DecimalField(decimal_places=0, max_digits=6)  
    instructorFeedback = models.CharField(max_length=200, default="")
    graded = models.BooleanField(default=False)
    numOfUploads = models.IntegerField(default = 0)
    
    richTextSubmission = models.CharField(max_length=20000, null=True, blank=True)
    comment = models.CharField(max_length=500, default="") #Comment submitted by the team
    def __str__(self):              
        return "{} : {} : {} : {}".format(self.teamActivityID, self.teamID, self.activityID, self.courseID)
    
# This model should logically go in Badges, but putting it there creates circular dependencies
class StudentPlayerType(models.Model):
    course = models.ForeignKey(Courses, on_delete=models.SET_NULL, null=True, verbose_name="the related course", db_index=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the student", db_index=True)
    playerType = models.ForeignKey(PlayerType, on_delete=models.CASCADE, verbose_name="the player type", db_index=True)
    def __str__(self):
        return "Student "+str(self.studen135pxt.user.username)+" has player type "+str(self.playerType.name)
# holds the customly made avatar
class StudentCustomAvatar(models.Model):
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the related student", db_index=True)
  
    faceIndex       = models.IntegerField(default=1)
    noseIndex       = models.IntegerField(default=1)
    mouthIndex      = models.IntegerField(default=1)
    eyeIndex        = models.IntegerField(default=1)
    eyebrowIndex    = models.IntegerField(default=1)
    eyewearIndex    = models.IntegerField(default=0)
    hairIndex       = models.IntegerField(default=1)
    fahairIndex     = models.IntegerField(default=0)
    clothesIndex    = models.IntegerField(default=1)
    backgroundIndex = models.IntegerField(default=1)
    
    faceColorIndex       = models.IntegerField(default=1)
    eyeColorIndex        = models.IntegerField(default=1)
    eyebrowColorIndex    = models.IntegerField(default=1)
    eyewearColorIndex    = models.IntegerField(default=1)
    hairColorIndex       = models.IntegerField(default=1)
    fahairColorIndex     = models.IntegerField(default=1)
    clothesColorIndex    = models.IntegerField(default=1)
    backgroundColorIndex = models.IntegerField(default=1)
    image = models.CharField(max_length=200, default='/static/images/generatedAvatarImages/default_profilePicture.png')
    def __str__(self):
        return str(self.studentID) 
class PendingVirtualApplause(models.Model): 
 
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="the related student", db_index=True)
    ApplauseOption = models.IntegerField(default=0)    