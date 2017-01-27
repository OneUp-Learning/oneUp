from datetime import datetime
from django.db import models
from Instructors.models import Courses, Challenges, Skills, Activities
from Badges.enums import Event, OperandTypes, SystemVariable, Action
from pip.cmdoptions import verbose


# Create your models here.
 
# Actions Table

#  Actions (Visible to instructors):
#  -    Giving a badge
#  -    Creating a notification
#  -    Locking
#  -    Unlocking 
#  -    Setting a value
#  -    Adding to a value
#   
#  Actions for event "Changing Values":
#  -    Adding skill points to skills

# Class removed and replaced with enumerated type
#class Actions(models.Model):
#    actionID = models.AutoField(primary_key=True)
#    actionName = models.CharField(max_length=30)
#    actionDescription = models.CharField(max_length=100)
#    def __str__(self):              
#        return str(self.actionID)+","+str(self.actionName)

 
# Conditions Table
class Conditions(models.Model):
    conditionID = models.AutoField(primary_key=True)
    operation = models.CharField(max_length=100) # ==, >, <, >=, <=, !=, AND, OR, NOT
    operand1Type = models.IntegerField() # 1. immediate value (integer), 2. reference to the same Condition table, 3. reference to float constant, 4. reference to string constant, 5. reference to SystemVariables table 
    operand1Value = models.IntegerField()
    operand2Type = models.IntegerField() # 1. immediate value (integer), 2. reference to the same Condition table, 3. reference to float constant, 4. reference to string constant, 5. reference to SystemVariables table 
    operand2Value = models.IntegerField()
    def __str__(self):
        def operandToString(type,value):
            if (type == OperandTypes.immediateInteger):
                return str(value)
            elif (type == OperandTypes.condition):
                return str(Conditions.objects.get(pk=value))
            elif (type == OperandTypes.floatConstant):
                return str(FloatConstants.objects.get(pk=value))
            elif (type == OperandTypes.stringConstant):
                return str(StringConstants.objects.get(pk=value))
            elif (type == OperandTypes.systemVariable): 
                if value in SystemVariable.systemVariables:
                    if 'name' in SystemVariable.systemVariables[value]:
                        return SystemVariable.systemVariables[value]['name']
                return "INVALID: Invalid SystemVariable value"
            return "INVALID: Invalid Operand Value."
        
        return "Cond#"+str(self.conditionID)+"("+operandToString(self.operand1Type,self.operand1Value)+" "+str(self.operation)+" "+operandToString(self.operand2Type,self.operand2Value)+')'

    # A simple method to clean up all objects associated with a condition
    # these can be assumed to be unique because we do not share references or any such
    # If we want to change to such a model to save database space, this would need to be changed. 
    def delete_children(self):
        def deleteOperand(type,value):
            if (type == OperandTypes.condition):
                childCond = Conditions.objects.get(pk=value)
                childCond.delete_children()
                childCond.delete()
            elif (type == OperandTypes.floatConstant):
                FloatConstants.objects.get(pk=value).delete()
            elif (type == OperandTypes.stringConstant):
                StringConstants.objects.get(pk=value).delete()
        deleteOperand(self.operand1Type,self.operand1Value)
        deleteOperand(self.operand2Type,self.operand2Value)
        
# Events Table

# -   Taking a test
#     o    Starting a test
#     o    Finishing a test
#     o    Completing  a question
# -   Instructor entering information for an activity
# -   Passing certain time
# -   Change value

# Events class removed and replaced with an enumerated type - Keith
#
#class Events(models.Model):
#    eventID = models.AutoField(primary_key=True)
#    eventName = models.CharField(max_length=30)
#    eventDescription = models.CharField(max_length=100)
#    def __str__(self):              
#        return str(self.eventID)+","+str(self.eventName)

# Rules Table
class Rules(models.Model):
    ruleID = models.AutoField(primary_key=True)
    conditionID = models.ForeignKey(Conditions, verbose_name="the related condition", db_index=True)
    actionID = models.IntegerField(verbose_name="the related action", db_index=True)
    courseID = models.ForeignKey(Courses, verbose_name="Course the rule belongs to", db_index=True)
    def __str__(self):
        if self.actionID in Action.actions:
            return "[Rule#:"+str(int(self.ruleID))+" When:"+str(self.conditionID)+" Do:"+Action.actions[self.actionID]['name']+']'
        else:
            return "INVALID: Action identifier is invalid"
    # Deletes all related objects.  Should be called before deleting a Rule.
    def delete_related(self):
        RuleEvents.objects.filter(rule=self).delete()
        self.conditionID.delete_children()
        self.conditionID.delete()
        
# A model which matches a Rule to a list of events
# Each entry is one matching
class RuleEvents(models.Model):
    rule = models.ForeignKey(Rules,db_index=True)
    event = models.IntegerField(default=0,db_index=True)
    def __str__(self):
        if self.event in Event.events:
            return "(Rule#:"+str(int(self.rule.ruleID))+":Event "+str(Event.events[self.event]["name"])+")"
        else:
            return "(Rule#:"+str(int(self.rule.ruleID))+":INVALID EVENT)"

        
# Action-Arguments Table
class ActionArguments(models.Model):
    ruleID = models.ForeignKey(Rules, verbose_name="the related rule", db_index=True)  
    sequenceNumber = models.IntegerField()
    argumentValue = models.CharField(max_length=100) #e.g. badgeID
    def __str__(self):              
        return str(self.ruleID) + str(self.sequenceNumber) +","+str(self.argumentValue) 
 
# Badges Table
class Badges(models.Model):
    badgeID = models.AutoField(primary_key=True)
    ruleID = models.ForeignKey(Rules, verbose_name="the related rule", db_index=True)
    #instructorID = models.ForeignKey(InstructorInfo, verbose_name="the related instructor Id", db_index=True)
    courseID = models.ForeignKey(Courses, verbose_name="the related course", db_index=True) # Remove this if using the instructor Id
    badgeName = models.CharField(max_length=30) # e.g. test score, number of attempts 
    badgeDescription = models.CharField(max_length=100)
    badgeImage = models.CharField(max_length=30)
    assignToChallenges = models.IntegerField() # 1. All, 2. Specific
    def __str__(self):              
        return "Badge#"+str(self.badgeID)+":"+str(self.badgeName)
     
# System Variables (standard variables for the Python methods) Table

# system variables and their operation type
# No. of attempts : Count
# Test Score : Average
# percentage of correct answers : Percentile
# Max. of test scores : Max
# Min. of test scores : Min
# Min. and Max. of test scores is the minimum or maximum test-score of all the student's attempts for a particular test. These variables can be used to see the improvement of the student between attempts. For eg. a test's total score is 100 and a student scores 10 in 1st attempt and 100 in another attempt, then, min of test scores - max of test scores = 90 is a great imrovement. 
# Time to submit test (time taken by a student to complete a test) : Subtraction (time_submitted - time_started)
# Date of attempting test (the date when student has attempted the test for first time)


# Class removed and replaced with enumerated type - Keith
#class SystemVariables(models.Model):
#    systemVariableID = models.AutoField(primary_key=True)
#    variableName = models.CharField(max_length=30) # e.g. test score, number of attempts, 
#    variableDescription = models.CharField(max_length=100)
#    readOnlyIndicator = models.BooleanField(default=True)
#    operation = models.CharField(max_length=100) # COUNT, MIN, MAX, SUM. we don't need this operation column as the system variables are predefined and instructor is going to choose only from these set of variables. So using the name of the variable we can know how are we going to calculate/achieve them in the python code.
#    def __str__(self):              
#        return str(self.systemVariableID)+","+str(self.variableName)
 
# Dates Table
class Dates(models.Model):
    dateID = models.AutoField(primary_key=True)
    dateValue = models.DateField() 
    def __str__(self):              
        return str(self.dateID)+","+str(self.dateValue)
 
# Float-Constants Table
class FloatConstants(models.Model):
    floatID = models.AutoField(primary_key=True)
    floatValue = models.DecimalField(decimal_places=2, max_digits=6)
    def __str__(self):              
        return "Float#"+str(self.floatID)+":"+str(self.floatValue)
 
# String-Constants Table
class StringConstants(models.Model):
    stringID = models.AutoField(primary_key=True)
    stringValue = models.CharField(max_length=100) 
    def __str__(self):
        return "String#"+str(self.stringID)+":'"+str(self.stringValue)+"'"
 
# Game Mechanics Table
class GameMechanics(models.Model):
    gameMechanismID = models.AutoField(primary_key=True)
    gameMechanismName = models.CharField(max_length=30) 
    gameMechanismDescription = models.CharField(max_length=100)
    def __str__(self):              
        return str(self.gameMechanismID)+","+str(self.gameMechanismName)
 
# Course Mechanics Table
class CourseMechanics(models.Model):
    courseID = models.ForeignKey(Courses, verbose_name="the related course", db_index=True)
    gameMechanismID = models.ForeignKey(GameMechanics, verbose_name="the related game mechanism", db_index=True) 
    def __str__(self):              
        return str(self.courseID)+","+str(self.gameMechanismID)

# This table has the information about the badges and assigned challenges
class BadgeChallenges(models.Model):
    badgeChallengeID = models.AutoField(primary_key=True)
    badgeID = models.ForeignKey(Badges, verbose_name="the related badge", db_index=True)
    challengeID = models.ForeignKey(Challenges, verbose_name="the related challenge", db_index=True)
    def __str__(self):              
        return str(self.badgeID)+","+str(self.challengeID)
     
# '''
# Course Configuration parameters (goes into Badges.models.py)
# -    Selecting to activate specific game mechanics rules (categories of rules)
# -    Should the system display "How far are they from a particular award"
# '''
class CourseConfigParams(models.Model):
    ccpID = models.AutoField(primary_key=True)
    courseID = models.ForeignKey(Courses, verbose_name="the related course", db_index=True)
    
    badgesUsed = models.BooleanField(default=False)                   ## The badgesUsed is for instructor dashboard purposes and system uses as well
    studCanChangeBadgeVis = models.BooleanField(default=False)        ## The studCanChangeBadgeVis is for allowing student to configure student dashboard visibility only
    numBadgesDisplayed = models.IntegerField(default=0)               ## This is used to display the number of students in the leaderboard dashboard html table

    levelingUsed = models.BooleanField(default=False)                 ## 

    leaderboardUsed = models.BooleanField(default=False)              ##
    studCanChangeLeaderboardVis = models.BooleanField(default=False)  ##
    numStudentsDisplayed = models.IntegerField(default=0)              ## This is used to display the number of students in the leaderboard dashboard html table


    classSkillsDisplayed = models.BooleanField(default=False)         ## The classSkillsDisplayed is only for dashboard purposes for the instructor
    studCanChangeClassSkillsVis = models.BooleanField(default=False)  ## The classSkillsDisplayed is only for dashboard purposes for the student
    numStudentBestSkillsDisplayed = models.IntegerField(default=0)    ## This is used to display the number of students in the Skills dashboard html table

    ## Other fields for rule based configurations
    virtualCurrencyUsed = models.BooleanField(default=False)          ## isCourseBucksDisplayed was renamed, this is used in individual achievements
    avatarUsed = models.BooleanField(default=False)                   ## This is to allow the student to upload an avatar.
    classAverageUsed = models.BooleanField(default=False)             ## ranga used this, in individual achievements
    studCanChangeclassAverageVis = models.BooleanField(default=False) ## The student can suppress visibility in the dashboard
    
    ##XP(Experience) Points
    courseStartDate=models.DateField(default=datetime.min)            ##
    courseEndDate=models.DateField(default=datetime.min)              ##
    leaderboardUpdateFreq=models.IntegerField(default=1)              ## Frequency in days, minimum 1 and maximum 365 days
    
    def __str__(self):
        return str(self.ccpID)  +","
        +str(self.courseID) +","
        +str(self.badgesUsed) +","
        +str(self.studCanChangeBadgeVis) +","
        +str(self.numBadgesDisplayed) +","
        +str(self.levelingUsed) +","
        +str(self.leaderboardUsed) +","
        +str(self.studCanChangeLeaderBoardVis) +","
        +str(self.numStudentsDisplayed) +","
        +str(self.classSkillsDisplayed) +","
        +str(self.studCanChangeClassSkillsVis) +","
        +str(self.numStudentBestSkillsDisplayed) +","
        +str(self.virtualCurrencyUsed) +","
        +str(self.avatarUsed) +","
        +str(self.classAverageUsed) +","
        +str(self.studCanChangeclassAverageVis) +","
        +str(self.courseStartDate) +","
        +str(self.courseEndDate) +","
        +str(self.leaderboardUpdateFreq)

# # '''
# # Configuration parameters
# # -    Selecting to activate specific game mechanics rules (categories of rules)
# # -    Should the system display "How far are they from a particular award"
# # '''
# 
# class CourseConfigParams(models.Model):
#     ccpID = models.AutoField(primary_key=True)
#     courseID = models.ForeignKey(Courses, verbose_name="the related course", db_index=True)
#     
#     badgesUsed = models.BooleanField(default=False)
#     latestBadgesUsed = models.BooleanField(default=False)
#     levellingUsed = models.BooleanField(default=False)
#     leaderBoardDisplayed = models.BooleanField(default=False)
#     leaderBoardUsed = models.BooleanField(default=False)
#     virtualCurrencyUsed = models.BooleanField(default=False) ## isCourseBucksDisplayed was renamed
#     avatarUsed = models.BooleanField(default=False)
#     classAverageUsed = models.BooleanField(default=False) ## ranga used this
#     #classRankingUsed = models.BooleanField(default=False)
#     numStudentToppersUsed = models.IntegerField(default=0)
#     numStudentBestSkillsUsed = models.IntegerField(default=0)
#     
# 
#     
#     def __str__(self):
#         return str(self.ccpID)  +","
#         +str(self.courseID) +","
#         +str(self.badgesUsed) +","
#         +str(self.latestBadgesUsed) +","
#         +str(self.levellingUsed) +","
#         +str(self.leaderBoardUsed) +","
#         +str(self.virtualCurrencyUsed) +","
#         +str(self.avatarUsed) +","
#         +str(self.classAverageUsed) +"," 
#         #+str(self.classRankingUsed) +","
#         +int(self.numStudentToppersUsed) +","
#         +int(self.numStudentBestSkillsUsed) 
#          
#         
#         #return str(self.ccpID)  +","+ str(self.courseID) +","+str(self.areBadgesDisplayed) +","+str(self.isLevellingDisplayed) +","+str(self.isLeaderBoardDisplayed) +","+str(self.isVirtualCurrencyDisplayed) +","+str(self.isAvatarDisplayed) +","+str(self.isClassAverageDisplayed)              
# 

        
