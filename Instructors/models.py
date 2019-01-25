import os

from django.db import models
from django import forms

from django.contrib.auth.models import User
from django.template.defaultfilters import default
from datetime import datetime
from Instructors.constants import uncategorized_activity, default_time_str

from django.conf.global_settings import MEDIA_URL
from oneUp.settings import MEDIA_ROOT, MEDIA_URL, BASE_DIR

from django_celery_beat.models import PeriodicTask

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
     #instrucorID = models.ForeignKey(InstructorInfo, verbose_name="the related instructor", db_index=True) 
    courseName = models.CharField(max_length=75)
    courseDescription=models.CharField(max_length=2000, default="")
   #semester = models.CharField(max_length=75) 
    def __str__(self):              
        return str(self.courseID) +","+ self.courseName
    
    
# Table listing all the Instructors and the respective courses they are currently administering    
class InstructorRegisteredCourses(models.Model):
    instructorID = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Instructor ID", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name = "Course Name", db_index=True)
    def __str__(self):
        return str(self.instructorID) + "," + str(self.courseID)
    
    
       
#class Difficulty(models.Model):
    #difficultyID = models.AutoField(primary_key=True)
    #difficulty = models.CharField(max_length=75, default="")
    #def __str__(self):              
        #return str(self.difficulty)

    
# class Topics(models.Model):
#     topicID = models.AutoField(primary_key=True)
#     topicName = models.CharField(max_length=75)
#     courseID = models.ForeignKey(Courses, verbose_name="the related course", db_index=True)  
#     def __str__(self):
#         return  str(self.topicID) +","+self.topicName

class Questions(models.Model):
    questionID = models.AutoField(primary_key=True)
    preview = models.CharField(max_length=200)
    instructorNotes = models.CharField(max_length=300)
    type = models.IntegerField(default=0)
    difficulty = models.CharField(max_length=50, default="")
    author = models.CharField(max_length=100, default="")  
#     topicID = models.ForeignKey(Topics, verbose_name="the related topic", db_index=True) 
#     courseID = models.ForeignKey(Courses, verbose_name="the related course", db_index=True)
    def __str__(self):              
        return str(self.questionID)+","+self.preview
    
class StaticQuestions(Questions):
    questionText = models.CharField(max_length=10000)
    correctAnswerFeedback = models.CharField(max_length=1000, default="")
    incorrectAnswerFeedback = models.CharField(max_length=1000, default="")
    
# class ParsonsQuestions(Questions):
#     questionText = models.CharField(max_length=10000)
#     modelSolution = models.CharField(max_length=20000)  # contains the codeLines entered by the instructors
    #codeLinePartialOrder = models.CharField(max_length=10000)  # contains a specification of partial order: for each codeLine - a list of lines that can possibly follow it directly
    #numberDistractors = models.IntegerField(default=0)    

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
    
class Goals(models.Model):    
    goalID = models.AutoField(primary_key=True)
    goalAuthor = models.CharField(max_length=75)
    goalsCol = models.CharField(max_length=75, default="")
    #...
    def __str__(self):
        return self.goalAuthor
        
class Challenges(models.Model):
    challengeID = models.AutoField(primary_key=True)
    challengeName = models.CharField(max_length=100)
    courseID = models.ForeignKey(Courses, on_delete=models.SET_NULL, null=True,verbose_name="the related course", db_index=True) 
    isGraded = models.BooleanField(default=False)
    isRandomized = models.BooleanField(default=False)
    totalScore = models.DecimalField(decimal_places=2, max_digits=6, default=0)  #Total score for the automatically graded part
    manuallyGradedScore = models.DecimalField(decimal_places=2, max_digits=6, default=0, verbose_name="number of possible points for a manually graded part of the challenge")  
    curve = models.DecimalField(decimal_places=2, max_digits=6, default=0) 
    numberAttempts = models.IntegerField()
    timeLimit = models.IntegerField(verbose_name="time limit for the challenge in minutes")
    #feedbackOption = models.IntegerField()
    displayCorrectAnswer = models.BooleanField(default=True)
    displayCorrectAnswerFeedback = models.BooleanField(default=False)
    displayIncorrectAnswerFeedback = models.BooleanField(default=False)
    challengeAuthor = models.CharField(max_length=75)
    challengeDifficulty = models.CharField(max_length=45, default="")
    isVisible = models.BooleanField(default=True)
    startTimestamp = models.DateTimeField(default=datetime.now, blank=True)
    endTimestamp = models.DateTimeField(default=datetime.now, blank=True)
    challengePassword = models.CharField(default='',max_length=30) # Empty string represents no password required.
    challengePosition = models.IntegerField(default = 0)
    dueDate = models.DateTimeField(default=datetime.now, blank=True)
    
    def __str__(self):              
        return str(self.challengeID)+","+self.challengeName       
    def getCombinedScore(self):
        score = self.totalScore + self.manuallyGradedScore 
        if score > 0:
            return score
        else:
            return 1
      
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
        return str(self.challengeID)+","+str(self.questionID)
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
    def __str__(self):
        return str(self.categoryID)+":"+self.name

class Activities(models.Model):
    activityID = models.AutoField(primary_key=True)
    activityName = models.CharField(max_length=75)
    description = models.CharField(max_length=200, default="")
    points =  models.DecimalField(decimal_places=3, max_digits=6, default=0)
    isGraded = models.BooleanField(default=False,verbose_name = "Activity points will be added to the course grade")
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name = "Course Name", db_index=True)  
    isFileAllowed = models.BooleanField(default = True)
    uploadAttempts = models.IntegerField(default=0)
    instructorNotes = models.CharField(max_length=300, default="")
    author = models.CharField(max_length=100) 
    startTimestamp = models.DateTimeField(default=datetime.now, blank=True)
    endTimestamp = models.DateTimeField(default=datetime.now, blank=True )
    deadLine = models.DateTimeField(default=datetime.now, blank=True)
    category = models.ForeignKey(ActivitiesCategory,on_delete=models.CASCADE, verbose_name = "Activities Category", db_index=True, default = 1)
    activityPosition = models.IntegerField(default = 0)
    def __str__(self):              
        return str(self.activityID)+","+self.activityName  
        
class Announcements(models.Model):
    announcementID = models.AutoField(primary_key=True)
    authorID = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Author", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name = "Course Name", db_index=True)
    startTimestamp = models.DateTimeField()
    endTimestamp = models.DateTimeField()
    subject = models.CharField(max_length=25, default="")
    message = models.CharField(max_length=1000, default="")
    def __str__(self):              
        return str(self.announcementID)+","+str(self.authorID)+","+str(self.startTimestamp)

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
    
class CoursesSubTopics(models.Model):
    subTopicID = models.AutoField(primary_key=True)
    topicID = models.ForeignKey('Instructors.Topics', on_delete=models.CASCADE, verbose_name="topic")    
    courseID = models.ForeignKey('Instructors.Courses', on_delete=models.CASCADE, verbose_name="courses")
    subTopicName = models.CharField(max_length=100)
    subTopicPos = models.IntegerField(default=0)
    thresholdXP = models.IntegerField(default=0)
    thresholdSP = models.IntegerField(default=0)
    displayDate = models.DateTimeField(default=datetime.now, blank=True)
    
    def __str__(self):              
        return str(self.courseID)+","+str(self.topicID)+","+str(self.subTopicID)

class ChallengesTopics(models.Model):
    topicID = models.ForeignKey('Instructors.Topics', on_delete=models.CASCADE, verbose_name="topic")
    challengeID = models.ForeignKey('Instructors.Challenges', on_delete=models.CASCADE, verbose_name="challenges")  
    def __str__(self):              
        return str(self.challengeID)+","+str(self.topicID)
    
class Milestones(models.Model):
    milestoneID = models.AutoField(primary_key=True)
    milestoneName = models.CharField(max_length=75)
    description = models.CharField(max_length=200, default="")
    points =  models.IntegerField()
    authorID = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Author", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name = "Course Name", db_index=True)
    def __str__(self):              
        return str(self.milestoneID)+","+self.milestoneName

def imageUploadPath(instance,filename):
    return os.path.join(os.path.join(os.path.abspath(MEDIA_ROOT), 'images/uploadedInstructorImages'),filename)

#Uploaded Images
class UploadedImages(models.Model):
    imageID = models.AutoField(primary_key=True)
    # image = models.ImageField(upload_to = 'images/uploadedInstructorImages', default = 'images/uploadedInstructorImages')
    imageFile = models.FileField(max_length=500, upload_to= imageUploadPath)
    imageFileName = models.CharField(max_length=200, default='')
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
        uploaded_at = models.DateTimeField(auto_now_add=True)
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
        uploaded_at = models.DateTimeField(auto_now_add=True)
        activityFileCreator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Creator", db_index=True)
        latest = models.BooleanField(default = True)
        
        def delete(self):
            super(UploadedActivityFiles, self).delete()
   
#Dynamic Questions Stuff
class DynamicQuestions(Questions):
    numParts = models.IntegerField(default=1)
    code = models.CharField(max_length=20000)

class TemplateDynamicQuestions(DynamicQuestions): 
    templateText = models.CharField(max_length=20000)
    setupCode = models.CharField(max_length=20000, default="")

    
class TemplateTextParts(models.Model):
    partNumber = models.IntegerField(default=1)
    dynamicQuestion = models.ForeignKey(TemplateDynamicQuestions,on_delete=models.CASCADE )
    templateText = models.CharField(max_length=20000)

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
    
class AttendaceStreakConfiguration(models.Model):
    streakConfigurationID = models.AutoField(primary_key=True)
    courseID = models.ForeignKey(Courses, on_delete=models.SET_NULL, null=True,verbose_name="the related course", db_index=True) 
    daysofClass = models.CharField(max_length=75)#days of the week that are class scheduled for semester
    daysDeselected = models.CharField(max_length=20000)#the days that were removed from the class schedule
    streakLength = models.IntegerField(default = 0)
    def __str__(self):              
        return str(self.streakConfigurationID)+","+str(self.courseID)+","+str(self.daysofClass) +","+ str(self.daysDeselected)
    