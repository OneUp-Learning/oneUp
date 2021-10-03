import os
from datetime import datetime
from decimal import Decimal

from django import forms
from django.conf.global_settings import MEDIA_URL
from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import default
from django.utils.timezone import now
from django_celery_beat.models import PeriodicTask

from oneUp.settings import BASE_DIR, MEDIA_ROOT, MEDIA_URL


def custom_now():
    return now().replace(microsecond=0)

# DO NOT USE (Instructors Table is replaced by general User table)
class Instructors(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True,default=0)
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
    # ----universityID = models.CharField(max_length=100)
    def __str__(self):              
        #return str(self.studentID)+","+self.name+self.name
        return str(self.user.username)
        
class Courses(models.Model):
    courseID = models.AutoField(primary_key=True)
    courseName = models.CharField(max_length=75)
    courseDescription = models.CharField(max_length=2000, default="")
     
    def __str__(self):              
        return self.courseName

class Universities(models.Model):
    universityID = models.AutoField(primary_key=True)
    universityName = models.CharField(max_length=300)
    universityDescription = models.CharField(max_length=2000, default="")
    universityTimezone = models.CharField(max_length=100, default="America/New_York")
    universityPostfix = models.CharField(max_length=100, default="")
    def __str__(self):              
        return f"{self.universityID} - {self.universityName} - {self.universityDescription} - {self.universityTimezone} - {self.universityPostfix}"
#Association table between instructors user table and Universities table
class InstructorToUniversities(models.Model):
    instructorID = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Instructor ID", db_index=True)
    universityID = models.ForeignKey(Universities, on_delete=models.CASCADE, verbose_name="the related university", db_index=True)
    def __str__(self):              
        return f"{self.instructorID} - {self.universityID}"

class UniversityCourses(models.Model):
    universityCourseID = models.AutoField(primary_key=True)
    universityID = models.ForeignKey(Universities, on_delete=models.CASCADE, null=True, verbose_name="Univerity", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, null=True, verbose_name = "Course", db_index=True)
    def __str__(self):
        return str(self.courseID)
    
# Table listing all the Instructors and the respective courses they are currently administering    
class InstructorRegisteredCourses(models.Model):
    instructorID = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Instructor ID", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name = "Course Name", db_index=True)
    Donations = models.IntegerField(default = 0)
    def __str__(self):
        return str(self.instructorID) + "," + str(self.courseID) 

class Questions(models.Model):
    questionID = models.AutoField(primary_key=True)
    preview = models.CharField(max_length=200)
    instructorNotes = models.CharField(max_length=300)
    type = models.IntegerField(default=0)
    difficulty = models.CharField(max_length=50, default="")
    author = models.CharField(max_length=100, default="")
    isHintUsed = models.BooleanField(default=False)
    basicHint = models.CharField(max_length=100, default="") 
    strongHint = models.CharField(max_length=100, default="")
#     courseID = models.ForeignKey(Courses, verbose_name="the related course", db_index=True)
    def __str__(self):              
        return f"{self.questionID} - {self.preview}"
class QuestionProgrammingFiles(models.Model):
    programmingFileID = models.AutoField(primary_key=True)
    questionID = models.ForeignKey(Questions, on_delete=models.CASCADE, null=True, verbose_name= 'the related question')
    programmingFileName = models.CharField(max_length=200)
    programmingFileFolderName = models.CharField(max_length=200)
    uploaded_at = models.DateTimeField(default=custom_now)
    programmingFileUploader = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name="Creator", db_index=True)
     
class StaticQuestions(Questions):
    questionText = models.CharField(max_length=10000)
    correctAnswerFeedback = models.CharField(max_length=1000, default="")
    incorrectAnswerFeedback = models.CharField(max_length=1000, default="") 

class CodeLibrary(models.Model):
    name = models.CharField(max_length=200)
    fileName = models.CharField(max_length=1000)
       
class Answers(models.Model):
    answerID = models.AutoField(primary_key=True)
    answerText = models.CharField(max_length=5000)
    questionID = models.ForeignKey(Questions, on_delete=models.CASCADE, verbose_name="the related question", db_index=True)
    def __str__(self):              
        return str(self.answerID)+","+self.answerText

class FeedbackType(models.Model):
    feedbackID = models.AutoField(primary_key=True)
    feedbackText = models.CharField(max_length=1000, default="")
    def __str__(self):
        return str(self.feedbackText)

class MatchingAnswers(models.Model):
    matchingAnswerID = models.AutoField(primary_key=True)
    matchingAnswerText = models.CharField(max_length=5000)
    answerID = models.ForeignKey(Answers, on_delete=models.CASCADE, verbose_name="the answer which this match goes with", db_index=True)
    questionID = models.ForeignKey(Questions, on_delete=models.CASCADE, verbose_name="the related question", db_index=True)
    def __str__(self):              
        return str(self.answerID)+","+self.matchingAnswerText
        
class CorrectAnswers(models.Model):
    questionID = models.ForeignKey('Instructors.Questions', on_delete=models.CASCADE, verbose_name="the question")    
    answerID = models.ForeignKey('Instructors.Answers', on_delete=models.CASCADE, verbose_name="the correct answer")
    def __str__(self):              
        return str(self.answerID)+","+str(self.questionID)
    
class Prompts(models.Model):
    promptID = models.AutoField(primary_key=True)
    promptText = models.CharField(max_length=5000, default="")
    questionID = models.ForeignKey(Questions, on_delete=models.CASCADE, verbose_name="the related question", db_index=True)
    answerID = models.ForeignKey('Instructors.Answers', on_delete=models.CASCADE, verbose_name="the correct answer for this prompt")
        
class Challenges(models.Model):
    challengeID = models.AutoField(primary_key=True)
    challengeName = models.CharField(max_length=100)
    courseID = models.ForeignKey(Courses, on_delete=models.SET_NULL, null=True,verbose_name="the related course", db_index=True)

    isGraded = models.BooleanField(default=False) # Is the challenge of type serious (true) or warmup (false) 

    isRandomized = models.BooleanField(default=False)

    totalScore = models.DecimalField(decimal_places=2, max_digits=6, default=0)  #Total score for the automatically graded part
    manuallyGradedScore = models.DecimalField(decimal_places=2, max_digits=6, default=0, verbose_name="number of possible points for a manually graded part of the challenge")  
    curve = models.DecimalField(decimal_places=2, max_digits=6, default=0) 

    numberAttempts = models.IntegerField()
    timeLimit = models.IntegerField(verbose_name="time limit for the challenge in minutes")

    displayCorrectAnswer = models.BooleanField(default=True)
    displayCorrectAnswerFeedback = models.BooleanField(default=False)
    displayIncorrectAnswerFeedback = models.BooleanField(default=False)

    challengeAuthor = models.CharField(max_length=75)
    challengeDifficulty = models.CharField(max_length=45, default="")
    isVisible = models.BooleanField(default=True)

    startTimestamp = models.DateTimeField(default=custom_now, blank=True)
    endTimestamp = models.DateTimeField(default=custom_now, blank=True)
    dueDate = models.DateTimeField(default=custom_now, blank=True)

    hasStartTimestamp = models.BooleanField(default=False) # Flags used to determine if the timestamp should be used or not
    hasEndTimestamp = models.BooleanField(default=False)
    hasDueDate = models.BooleanField(default=False)

    challengePassword = models.CharField(default='',max_length=30) # Empty string represents no password required.
    challengePosition = models.IntegerField(default = 0)
    
    isTeamChallenge = models.BooleanField(default=False)
    
    def __str__(self):              
        return f"{self.challengeID} - {self.challengeName}"

    def getCombinedScore(self):
        score = self.totalScore + self.manuallyGradedScore 
        if score > 0:
            return score
        else:
            return Decimal(1)
      
class Skills(models.Model):
    skillID = models.AutoField(primary_key=True)
    skillName = models.CharField(max_length=100)
    skillAuthor = models.CharField(max_length=75)
    def __str__(self):              
        return str(self.skillID)+","+str(self.skillName)+","+str(self.skillAuthor)  #skillAuthor was missing

# Total earned points for a skill in a course
class CoursesSkills(models.Model):
    skillID = models.ForeignKey('Instructors.Skills', on_delete=models.CASCADE, verbose_name="skill")    
    courseID = models.ForeignKey('Instructors.Courses', on_delete=models.CASCADE, verbose_name="courses")
    def __str__(self):              
        return str(self.courseID)+","+str(self.skillID)

# Contributed points of a question to a skill in the context of a particular challenge --->  courseID should be replaced by challengeID
class QuestionsSkills(models.Model):
    skillID = models.ForeignKey('Instructors.Skills', on_delete=models.CASCADE, verbose_name="skill")    
    questionID = models.ForeignKey('Instructors.Questions', on_delete=models.CASCADE, verbose_name="questions")
    courseID = models.ForeignKey('Instructors.Courses', on_delete=models.CASCADE, verbose_name="courses", default=-1)    
    questionSkillPoints =  models.IntegerField(default=1)
    def __str__(self):              
        return "QuestionSkill: {Question:("+str(self.questionID)+"),Skill:("+str(self.skillID)+"),Course:("+str(self.courseID)+"),points:"+str(self.questionSkillPoints)+"}"

class Tags(models.Model):
    tagID = models.AutoField(primary_key=True)
    tagName = models.CharField(max_length=75, default="")
    def __str__(self):              
        return str(self.tagID)+","+self.tagName


class ResourceTags(models.Model): 
    questionID = models.ForeignKey('Instructors.Questions', on_delete=models.CASCADE, verbose_name="question")
    tagID = models.ForeignKey('Instructors.Tags', on_delete=models.CASCADE, verbose_name="tag")  
    def __str__(self):              
        return str(self.questionID) +","+ str(self.tagID)
      
class ChallengeTags(models.Model): 
    challengeID = models.ForeignKey('Instructors.Challenges', on_delete=models.CASCADE, verbose_name="challenge")
    tagID = models.ForeignKey('Instructors.Tags', on_delete=models.CASCADE, verbose_name="tag")  
    def __str__(self):              
        return str(self.challengeID) +","+ str(self.tagID)
    
class ChallengesQuestions(models.Model):
    challengeID = models.ForeignKey('Instructors.Challenges', on_delete=models.CASCADE, verbose_name="challenge")
    questionID = models.ForeignKey('Instructors.Questions', on_delete=models.CASCADE, verbose_name="question")
    questionPosition = models.IntegerField(default = 0)
    points = models.DecimalField(decimal_places=2, max_digits=6, default=0)
    def __str__(self):              
        return f"{self.pk} - {self.challengeID} - {self.questionID} - {self.points}"
        
    @staticmethod
    def addQuestionToChallenge(question, challenge, points, position):
        cq = ChallengesQuestions()
        cq.challengeID = challenge
        cq.questionID = question
        cq.points = points
        cq.questionPosition = position
        cq.save()
        return cq



class ActivitiesCategory(models.Model):
    categoryID = models.AutoField(primary_key=True)
    name = models.CharField(max_length=75)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name = "Course Name", db_index=True)
    xpWeight = models.DecimalField(decimal_places=3, max_digits=6, default=1) # This is a multiplier that is used when calculating XP for each category
    catPosition = models.IntegerField(default = 0)
    def __str__(self):
        return str(self.categoryID)+":"+self.name + ":" + str(self.xpWeight)

class Activities(models.Model):
    activityID = models.AutoField(primary_key=True)
    courseID = models.ForeignKey(Courses,on_delete=models.CASCADE, verbose_name = "Course Name", db_index=True) 

    activityName = models.CharField(max_length=75)
    description = models.CharField(max_length=2000, default="")

    points =  models.DecimalField(decimal_places=3, max_digits=6, default=0)

    isGraded = models.BooleanField(default=False,verbose_name = "Activity points will be added to the course grade")
     
    isFileAllowed = models.BooleanField(default = True)
    uploadAttempts = models.IntegerField(default=0)

    instructorNotes = models.CharField(max_length=300, default="")
    author = models.CharField(max_length=100) 

    startTimestamp = models.DateTimeField(default=custom_now, blank=True)
    endTimestamp = models.DateTimeField(default=custom_now, blank=True )
    deadLine = models.DateTimeField(default=custom_now, blank=True)

    hasStartTimestamp = models.BooleanField(default=False) # Flags used to determine if the timestamp should be used or not
    hasEndTimestamp = models.BooleanField(default=False)
    hasDeadline = models.BooleanField(default=False)

    category = models.ForeignKey(ActivitiesCategory,on_delete=models.CASCADE, verbose_name = "Activities Category", db_index=True, default = 1)
    activityPosition = models.IntegerField(default = 0)
    
    isAvailable = models.BooleanField(default=True,verbose_name = "Activity is available for students to see.")
    def __str__(self):              
        return f"{self.activityID} - {self.activityName} - {self.points} - {self.category} - {self.isGraded} - {self.isAvailable}" 
        
class Announcements(models.Model):
    announcementID = models.AutoField(primary_key=True)
    authorID = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Author", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name = "Course Name", db_index=True)

    startTimestamp = models.DateTimeField(default=custom_now)
    endTimestamp = models.DateTimeField(default=custom_now)

    hasStartTimestamp = models.BooleanField(default=False) # Flags used to determine if the timestamp should be used or not
    hasEndTimestamp = models.BooleanField(default=False)

    subject = models.CharField(max_length=100, default="")
    message = models.CharField(max_length=1000, default="")
    def __str__(self):              
        return f"{self.announcementID} - {self.authorID} - {self.startTimestamp} - {self.subject}"

class Topics(models.Model):
    topicID = models.AutoField(primary_key=True)
    topicName = models.CharField(max_length=100)
    def __str__(self):              
        return str(str(self.topicID)+","+self.topicName)
    
class CoursesTopics(models.Model):
    topicID = models.ForeignKey('Instructors.Topics', on_delete=models.CASCADE, verbose_name="topic")    
    courseID = models.ForeignKey('Instructors.Courses', on_delete=models.CASCADE, verbose_name="courses")
    topicPos = models.IntegerField(default=0)
    def __str__(self):              
        return str(self.courseID)+","+str(self.topicID)+","+str(self.topicPos)

class ChallengesTopics(models.Model):
    topicID = models.ForeignKey('Instructors.Topics', on_delete=models.CASCADE, verbose_name="topic")
    challengeID = models.ForeignKey('Instructors.Challenges', on_delete=models.CASCADE, verbose_name="challenges")  
    def __str__(self):              
        return str(self.challengeID)+","+str(self.topicID)

def imageUploadPath(instance,filename):
    return os.path.join(os.path.join(os.path.abspath(MEDIA_ROOT), 'images/uploadedInstructorImages'),filename)

#Uploaded Images
class UploadedImages(models.Model):
    imageID = models.AutoField(primary_key=True)
    imageFile = models.FileField(max_length=500, upload_to= 'images/uploadedInstructorImages')
    imageDescription = models.CharField(max_length=200, default='')
    imageCreator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Creator", db_index=True)

    def __str__(self):              
        return str(self.imageID)+","+str(self.imageFile)+","+self.imageDescription
    
    def delete(self):
        self.imageFile.delete()
        super(UploadedImages, self).delete()

def fileUploadPath(instance,filename):
    return os.path.join(os.path.join(os.path.abspath(MEDIA_ROOT), 'textfiles/xmlfiles'),filename)

#class for Uploaded Files
class UploadedFiles(models.Model):
        uploadedFile = models.FileField(max_length=500,upload_to= fileUploadPath)
        uploadedFileName = models.CharField(max_length=200, default='')
        uploaded_at = models.DateTimeField(default=custom_now)
        uploadedFileCreator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Creator", db_index=True)
        
        def delete(self):
            self.uploadedFile.delete()
            super(UploadedFiles, self).delete()
 

def activityUploadPath(instance,filename):
        return os.path.join(os.path.join(os.path.abspath(MEDIA_ROOT), 'Instructors/instructorActivityFiles'),filename)
            
class UploadedActivityFiles(models.Model):
        ID = models.AutoField(primary_key=True)
        activity = models.ForeignKey(Activities, on_delete=models.SET_NULL, null=True, verbose_name= 'the related activity')
        activityFile = models.FileField(max_length=500,upload_to= activityUploadPath)
        activityFileName = models.CharField(max_length=200, default='')
        uploaded_at = models.DateTimeField(default=custom_now)
        activityFileCreator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Creator", db_index=True)
        latest = models.BooleanField(default = True)
        
        def delete(self):
            super(UploadedActivityFiles, self).delete()
   
#Dynamic Questions Stuff
class DynamicQuestions(Questions):
    numParts = models.IntegerField(default=1)
    code = models.CharField(max_length=20000)
    submissionsAllowed = models.IntegerField(default=1, verbose_name="Number of Submissions Allowed")
    resubmissionPenalty = models.IntegerField(default=10, verbose_name="Resubmission penalty as an integer percentage")

class TemplateDynamicQuestions(DynamicQuestions): 
    templateText = models.CharField(max_length=20000)
    setupCode = models.CharField(max_length=20000, default="")
    
class TemplateTextParts(models.Model):
    partNumber = models.IntegerField(default=1)
    dynamicQuestion = models.ForeignKey(TemplateDynamicQuestions,on_delete=models.CASCADE )
    templateText = models.CharField(max_length=20000)
    pointsInPart = models.IntegerField(default=1, verbose_name="Points in this Part")

def luaLibraryUploadLocation(instance,filename):
    return os.path.join(os.path.join(os.path.abspath(MEDIA_ROOT), 'lua/uploadedLuaLibs'), filename)

class LuaLibrary(models.Model):
    libID = models.AutoField(primary_key=True)
    libFile = models.FileField(max_length=5000, upload_to= luaLibraryUploadLocation )
    libraryName = models.CharField(max_length=100, db_index=True, unique=True)
    libDescription = models.CharField(max_length=200, default='')
    libCreator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Creator", db_index=True)
    def __str__(self):              
        return str(self.libraryName)+","+self.libDescription
    
    def delete(self):
        self.libFile.delete()
        super(LuaLibrary, self).delete()
    def removeFile(self):
        self.libFile.delete()
        
class DependentLibrary(models.Model):
    dependID = models.AutoField(primary_key=True) 
    mainLibrary = models.ForeignKey(LuaLibrary, on_delete=models.CASCADE, related_name='mainLibrary')
    dependent = models.ForeignKey(LuaLibrary, on_delete=models.CASCADE)
  
class QuestionLibrary(models.Model):  
    ID = models.AutoField(primary_key=True) 
    question = models.ForeignKey(Questions, on_delete=models.CASCADE)
    library = models.ForeignKey(LuaLibrary, on_delete=models.CASCADE)

class FlashCards(models.Model):
    flashID = models.AutoField(primary_key=True)
    flashName = models.CharField(max_length=200,default='Flashcard') 
    front = models.CharField(max_length=5000)
    back = models.CharField (max_length=5000)
    def __str__(self):              
        return str(self.flashID)+","+self.flashName+","+self.front+","+self.back
class FlashCardGroup(models.Model):
    groupID = models.AutoField(primary_key=True)
    groupName = models.CharField(max_length=500)
    def __str__(self):              
        return str(self.groupID)+","+self.groupName
        
class FlashCardToGroup(models.Model):
    groupID = models.ForeignKey(FlashCardGroup,on_delete=models.CASCADE, db_index=True)
    flashID = models.ForeignKey(FlashCards,on_delete=models.CASCADE, db_index=True) 
    def __str__(self):              
        return str(self.flashID)+","+str(self.groupID)
class FlashCardGroupCourse(models.Model):
    groupID = models.ForeignKey(FlashCardGroup,on_delete=models.CASCADE,verbose_name ="Group Name", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name = "Course Name", db_index=True)
    availabilityDate=models.DateTimeField(default=now, blank=True)
    hasAvailabilityDate = models.BooleanField(default = False)
    groupPos = models.IntegerField(default=0)
    def __str__(self):              
        return str(self.groupID)+","+str(self.courseID)+","+str(self.availabilityDate)
