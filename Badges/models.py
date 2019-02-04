from datetime import datetime
from django.db import models
from Instructors.models import Courses, Challenges, Skills, Activities, Topics, ActivitiesCategory
from Badges.enums import Event, OperandTypes, Action, AwardFrequency
from Badges.systemVariables import SystemVariable
from Badges.periodicVariables import PeriodicVariables
from django_celery_beat.models import PeriodicTask

# Conditions Table
class Conditions(models.Model):
    conditionID = models.AutoField(primary_key=True)
    operation = models.CharField(max_length=100) # =, >, <, >=, <=, !=, AND, OR, NOT, FOR_ALL, FOR_ANY
    operand1Type = models.IntegerField() # See OperandTypes in Badges/enums.py for an explanation of meaning.
    operand1Value = models.IntegerField()
    operand2Type = models.IntegerField() # See OperandTypes in Badges/enums.py for an explanation of meaning.
    operand2Value = models.IntegerField()
    courseID = models.ForeignKey(Courses, verbose_name = "The course this condition belongs to", db_index=True, on_delete=models.CASCADE, default=0)
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
            elif (type == OperandTypes.boolean):
                return str(1 == value)
            elif (type == OperandTypes.dateConstant):
                return str(Dates.objects.get(pk=value))
            elif (type == OperandTypes.systemVariable): 
                if value in SystemVariable.systemVariables:
                    if 'name' in SystemVariable.systemVariables[value]:
                        return SystemVariable.systemVariables[value]['name']
                return "INVALID: Invalid SystemVariable value"
            elif (type == OperandTypes.challengeSet):
                if value == 0:
                    return "All challenges"
                else:
                    output = "Challenge Set {"
                    for challengeSet in ChallengeSet.objects.filter(condition=self):
                        output += str(challengeSet.challenge) + ','
                    output += '}'
                    return output
            elif (type == OperandTypes.activitySet):
                if value == 0:
                    return "All activities"
                else:
                    output = "Activity Set {"
                    for activitySet in ActivitySet.objects.filter(condition=self):
                        output += str(activitySet.activity) + ','
                    output += '}'
                    return output
            elif (type == OperandTypes.conditionSet):
                output = "Condition Set {"
                for conditionSet in ConditionSet.objects.filter(parentCondition=self):
                    output += str(conditionSet.conditionInSet.conditionID) + ','
                output += '}'
                return output
            elif (type == OperandTypes.noOperand):
                return ''
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
    conditionID = models.ForeignKey(Conditions, on_delete=models.SET_NULL, verbose_name="the related condition", db_index=True, null=True, blank=True)
    actionID = models.IntegerField(verbose_name="the related action", db_index=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="Course the rule belongs to", db_index=True)
    objectSpecifier = models.CharField(max_length=2000, default="[]",verbose_name="A json-serialized object of the type ChosenObjectSpecifier (see events.py)")
    awardFrequency = models.IntegerField(default=AwardFrequency.justOnce) # See enums.py for award frequency options.
    def __str__(self):
        if self.actionID in Action.actions:
            return "[Rule#:"+str(int(self.ruleID))+" When:"+str(self.conditionID)+" Do:"+Action.actions[self.actionID]['name']+']'
        else:
            return "INVALID: Action identifier is invalid"
    # Deletes all related objects.  Should be called before deleting a Rule.
    def delete_related(self):
        RuleEvents.objects.filter(rule=self).delete()
        ActionArguments.objects.filter(ruleID = self).delete()
        self.conditionID.delete_children()
        self.conditionID.delete()
        
# A model which matches a Rule to a list of events
# Each entry is one matching
class RuleEvents(models.Model):
    rule = models.ForeignKey(Rules,on_delete=models.CASCADE, db_index=True)
    event = models.IntegerField(default=0,db_index=True)
    inGlobalContext = models.BooleanField(default=True)
    def __str__(self):
        if self.event in Event.events:
            context = "global" if self.inGlobalContext else "local"
            return "(Rule#:"+str(int(self.rule.ruleID))+" is triggered by Event "+str(Event.events[self.event]["name"])+" in a "+context+" context)"
        else:
            return "(Rule#:"+str(int(self.rule.ruleID))+" is triggered by INVALID EVENT)"

        
# Action-Arguments Table
class ActionArguments(models.Model):
    ruleID = models.ForeignKey(Rules, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="the related rule", db_index=True)  
    sequenceNumber = models.IntegerField()
    argumentValue = models.CharField(max_length=100) #e.g. badgeID
    def __str__(self):              
        return str(self.ruleID) + str(self.sequenceNumber) +","+str(self.argumentValue) 

# Table for the manually assigned badges
class BadgesInfo(models.Model):
    badgeID = models.AutoField(primary_key=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="the related course", db_index=True) # Remove this if using the instructor Id
    badgeName = models.CharField(max_length=300) # e.g. test score, number of attempts 
    badgeDescription = models.CharField(max_length=10000)
    badgeImage = models.CharField(max_length=300)
    manual = models.BooleanField(default=False) #TODO: Reconstruct badges types (automatic, manual, perioidic)
    badgePosition = models.IntegerField(default=0) # The position a badge should be displayed to everyone 
    isPeriodic = models.BooleanField(default=False) # Is this badge info for a periodic badge
    def __str__(self):              
        return "Badge#"+str(self.badgeID)+":"+str(self.badgeName)

# Badges Table    
class Badges(BadgesInfo):
#    badgeID = models.AutoField(primary_key=True)
    ruleID = models.ForeignKey(Rules,  on_delete=models.SET_NULL, null=True, blank=True, verbose_name="the related rule", db_index=True)
#    courseID = models.ForeignKey(Courses, verbose_name="the related course", db_index=True) # Remove this if using the instructor Id
#    badgeName = models.CharField(max_length=300) # e.g. test score, number of attempts 
#    badgeDescription = models.CharField(max_length=10000)
#    badgeImage = models.CharField(max_length=300)
    def __str__(self):              
        return "Badge#"+str(self.badgeID)+":"+str(self.badgeName)    

# Table for Periodic Badges
class PeriodicBadges(BadgesInfo):
    periodicVariableID = models.IntegerField() # The Perioidc Variable index set for this badge
    timePeriodID = models.IntegerField() # The Time Period index set for this badge
    periodicType = models.IntegerField(default=0) # The type of selected: TopN (0), All(1), Random(2)
    numberOfAwards = models.IntegerField(default=1, null=True) # The top number of students to award this badge to
    threshold = models.IntegerField(default=1) # The cutoff number of the result of the periodic variable function 
    operatorType = models.CharField(default='=', max_length=2) # The operator for the threshold (>=, >, =)
    isRandom = models.NullBooleanField(default=False) # Is this being awarded to random student(s)
    lastModified = models.DateTimeField(default=datetime.now) # The last time this rule was modified. Used to properly calculate periodic variables when first starting
    periodicTask = models.ForeignKey(PeriodicTask,  null=True, blank=True, on_delete=models.CASCADE, verbose_name="the periodic task", db_index=True) # The celery Periodic Task object
    
    def delete(self, *args, **kwargs):
        ''' Custom delete method which deletes the PeriodicTask object before deleting the badge.'''
        self.periodicTask.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return "Badge #{} : {}".format(self.badgeID, self.badgeName)

# Virtual Currency Table for both automatically and manually handled VC rules
class VirtualCurrencyCustomRuleInfo(models.Model):
    vcRuleID = models.AutoField(primary_key=True)
    vcRuleName = models.CharField(max_length=300) # e.g. test score, number of attempts 
    vcRuleDescription = models.CharField(max_length=4000)
    vcRuleType = models.BooleanField(default=True) # True: earning , False: spending    
    vcRuleAmount = models.IntegerField()
    vcRuleLimit = models.IntegerField(default=0) # (Spending Rules) set a limit to how many times this rule/item can be bought in the course shop
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="the related course", db_index=True) # Remove this if using the instructor Id
    isPeriodic = models.BooleanField(default=False) # this is info for a periodic virtual currency
    vcRulePosition = models.IntegerField(default=0) # The position a vcRule should be displayed to everyone 
    def __str__(self):
        return "VirtualCurrencyCustomRuleInfo#"+str(self.vcRuleID)+":"+str(self.vcRuleName)+":"+str(self.vcRuleAmount)

# Virtual Currency Table for the automatically handled VC rules
class VirtualCurrencyRuleInfo(VirtualCurrencyCustomRuleInfo):
    ruleID = models.ForeignKey(Rules, on_delete=models.SET_NULL, verbose_name="the related rule", db_index=True, null=True, blank=True)
    def __str__(self):              
        return "VirtualCurrencyRule#"+str(self.vcRuleID)+":"+str(self.vcRuleName)

# Table for Periodic Virtual Currency Rules
class VirtualCurrencyPeriodicRule(VirtualCurrencyCustomRuleInfo):
    periodicVariableID = models.IntegerField() # The Perioidc Variable index set for this rule
    timePeriodID = models.IntegerField() # The Time Period index set for this rule
    periodicType = models.IntegerField(default=0) # The type of selected: TopN (0), All(1), Random(2)
    numberOfAwards = models.IntegerField(default=1, null=True) # The top number of students to award this rule to
    threshold = models.IntegerField(default=1) # The cutoff number of the result of the periodic variable function 
    operatorType = models.CharField(default='=', max_length=2) # The operator for the threshold (>=, >, =)
    isRandom = models.NullBooleanField(default=False) # Is this being awarded to random student(s)
    lastModified = models.DateTimeField(default=datetime.now) # The last time this rule was modified. Used to properly calculate periodic variables when first starting
    periodicTask = models.ForeignKey(PeriodicTask, null=True, blank=True, on_delete=models.CASCADE, verbose_name="the periodic task", db_index=True) # The celery Periodic Task object

    def delete(self, *args, **kwargs):
        ''' Custom delete method which deletes the PeriodicTask object before deleting the rule.'''
        self.periodicTask.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return "VirtualCurrencyRule #{} : {}".format(self.vcRuleID, self.vcRuleName)

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
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="the related course", db_index=True)
    gameMechanismID = models.ForeignKey(GameMechanics, on_delete=models.CASCADE, verbose_name="the related game mechanism", db_index=True) 
    def __str__(self):              
        return str(self.courseID)+","+str(self.gameMechanismID)

# This table has the information about the badges and assigned challenges
#class BadgeChallenges(models.Model):
#    badgeChallengeID = models.AutoField(primary_key=True)
#    badgeID = models.ForeignKey(Badges, verbose_name="the related badge", db_index=True)
#    challengeID = models.ForeignKey(Challenges, verbose_name="the related challenge", db_index=True)
#    def __str__(self):              
#        return str(self.badgeID)+","+str(self.challengeID)
    
# '''
# Course Configuration parameters (goes into Badges.models.py)
# -    Selecting to activate specific game mechanics rules (categories of rules)
# -    Should the system display "How far are they from a particular award"
# '''
   
   
class LeaderboardsConfig(models.Model):
    leaderboardID = models.AutoField(primary_key=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="the related course", db_index=True) # Remove this if using the instructor Id
    leaderboardName = models.CharField(max_length=300) # e.g. test score, number of attempts 
    leaderboardDescription = models.CharField(max_length=10000)
    isContinous = models.BooleanField(default=False)
    isXpLeaderboard = models.BooleanField(default=False)
    numStudentsDisplayed = models.IntegerField(default=0) 
    periodicVariable = models.IntegerField(default=0)              ## This is used to display the number of students in the leaderboard dashboard html table
    timePeriodUpdateInterval = models.IntegerField(default=0000)                  # The Time Period index set for updating this leaderboard
    displayOnCourseHomePage = models.BooleanField(default=False)       # true=display on course home page; false=display on leaderbordas page 
    lastModified = models.DateTimeField(default=datetime.now) # The last time this rule was modified. Used to properly calculate periodic variables when first starting
    periodicTask = models.ForeignKey(PeriodicTask,  null=True, blank=True, on_delete=models.CASCADE, verbose_name="the periodic task", db_index=True) # The celery Periodic Task object
    howFarBack = models.IntegerField(default=0000)
    def __str__(self):              
        return "Leaderboard#"+str(self.leaderboardID)+":"+str(self.leaderboardName)   
   
class CourseConfigParams(models.Model):
    ccpID = models.AutoField(primary_key=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="the related course", db_index=True)

    gamificationUsed = models.BooleanField(default=False) 
    courseAvailable = models.BooleanField(default=True)               ## Is the course open or closed?
    badgesUsed = models.BooleanField(default=False)                   ## The badgesUsed is for instructor dashboard purposes and system uses as well
    studCanChangeBadgeVis = models.BooleanField(default=False)        ## The studCanChangeBadgeVis is for allowing student to configure student dashboard visibility only
    numBadgesDisplayed = models.IntegerField(default=0)               ## This is used to display the number of students in the leaderboard dashboard html table

    levelingUsed = models.BooleanField(default=False)                 ##
    
    classmatesChallenges = models.BooleanField(default=False)         ## This is used for duels and call-outs
    vcDuel = models.IntegerField(default=0)                           ## Amount of virtual currency rewarded to duel winners
    vcCallout = models.IntegerField(default=0)                        ## Amount of virtual currency rewarded to call-outs participants

    progressBarUsed = models.BooleanField(default=True)               ## This is the progress bar in the student achievements page
    
    chatUsed = models.BooleanField(default=True)                      ## This will enable or disable the chat feature 

    seriousChallengesGrouped = models.BooleanField(default=False)     ## Show the serious challenges grouped by topics similar to warmup challenges on the instructor side

    leaderboardUsed = models.BooleanField(default=False)              ##
    studCanChangeLeaderboardVis = models.BooleanField(default=False)  ##
    numStudentsDisplayed = models.IntegerField(default=0)             ## This is used to display the number of studentss in the leaderboard dashboard html table

    classSkillsDisplayed = models.BooleanField(default=False)         ## The classSkillsDisplayed is only for dashboard purposes for the instructor
    studCanChangeClassSkillsVis = models.BooleanField(default=False)  ## The classSkillsDisplayed is only for dashboard purposes for the student
    numStudentBestSkillsDisplayed = models.IntegerField(default=0)    ## This is used to display the number of students in the Skills dashboard html table

    ## Other fields for rule based configurations
    virtualCurrencyUsed = models.BooleanField(default=False)          ## isCourseBucksDisplayed was renamed, this is used in individual achievements
    virtualCurrencyAdded = models.IntegerField(default=0)             # Amount of course bucks given by the instructor to all students
    avatarUsed = models.BooleanField(default=False)                   ## This is to allow the student to upload an avatar.
    classAverageUsed = models.BooleanField(default=False)             ## ranga used this, in individual achievements
    studCanChangeclassAverageVis = models.BooleanField(default=False) ## The student can suppress visibility in the dashboard

    ##Misc Leaderboard Fields
    courseStartDate=models.DateField(default=datetime.min)            ##
    courseEndDate=models.DateField(default=datetime.min)              ##
    leaderboardUpdateFreq=models.IntegerField(default=1)              ## Frequency in days, minimum 1 and maximum 365 days
    ##XP Weights CalcualtionFields
    xpWeightSP = models.IntegerField(default=0)                       ## XP Weights for Skill Points
    xpWeightSChallenge = models.IntegerField(default=0)               ## XP Weights for Serious Challenges
    xpWeightWChallenge = models.IntegerField(default=0)               ## XP Weights for Warm up Challenges
    xpWeightAPoints    = models.IntegerField(default=0)               ## XP Weights for Activity Points

    ## Levels of Difficulties for the course
    thresholdToLevelMedium = models.IntegerField(default=0)           ## Thresholds in %  of previous level for moving from Easy (default level) to Medium
    thresholdToLevelDifficulty = models.IntegerField(default=0)       ## Thresholds in %  of previous level for moving from Medium (default level) to Hard

    def __str__(self):
        return "id:"+str(self.ccpID)  +", course:"+str(self.courseID) +", badges:"+str(self.badgesUsed) +",studcanchangebadgevis:" \
        +str(self.studCanChangeBadgeVis) +"," \
        +str(self.numBadgesDisplayed) +"," \
        +str(self.levelingUsed) +"," \
        +str(self.leaderboardUsed) +"," \
        +str(self.numStudentsDisplayed) +"," \
        +str(self.classSkillsDisplayed) +"," \
        +str(self.studCanChangeClassSkillsVis) +"," \
        +str(self.numStudentBestSkillsDisplayed) +"," \
        +str(self.virtualCurrencyUsed) +"," \
        +str(self.avatarUsed) +"," \
        +str(self.classAverageUsed) +"," \
        +str(self.studCanChangeclassAverageVis) +"," \
        +str(self.courseStartDate) +"," \
        +str(self.courseEndDate) +"," \
        +str(self.leaderboardUpdateFreq) +"," \
        +str(self.xpWeightSP) +"," \
        +str(self.xpWeightSChallenge) +"," \
        +str(self.xpWeightWChallenge) +"," \
        +str(self.xpWeightAPoints) +"," 
 
class ChallengeSet(models.Model):
    condition = models.ForeignKey(Conditions,verbose_name="the condition this set goes with",db_index=True,on_delete=models.CASCADE)
    challenge = models.ForeignKey(Challenges,verbose_name="the challenge included in the set",db_index=True,on_delete=models.CASCADE)
    def __str__(self):
        return "ChallengeSet for Condition: "+str(self.condition)+" includes Challenge: "+str(self.challenge)
     
class ActivitySet(models.Model):
    condition = models.ForeignKey(Conditions,verbose_name="the condition this set goes with",db_index=True,on_delete=models.CASCADE)
    activity = models.ForeignKey(Activities,verbose_name="the activity included in the set",db_index=True,on_delete=models.CASCADE)
    def __str__(self):
        return "ActivitySet for Condition: "+str(self.condition)+" includes Activity: "+str(self.activity)
    
class ConditionSet(models.Model):
    parentCondition = models.ForeignKey(Conditions,verbose_name="the condition this set goes with",db_index=True,on_delete=models.CASCADE,
                                        related_name="parentCondition")
    conditionInSet = models.ForeignKey(Conditions,verbose_name="the condition which is part of this set",db_index=True,on_delete=models.CASCADE)
    def __str__(self):
        return "ConditionSet for Condition: "+str(self.parentCondition)+" includes Condition: "+str(self.conditionInSet)
    
class TopicSet(models.Model):
    condition = models.ForeignKey(Conditions,verbose_name="the condition this set goes with",db_index=True,on_delete=models.CASCADE)
    topic = models.ForeignKey(Topics,verbose_name="the topic included in the set",db_index=True,on_delete=models.CASCADE)
    def __str__(self):
        return "TopicSet for Condition: "+str(self.condition)+" includes Topic: "+str(self.topic)
    
class ActivityCategorySet(models.Model):
    condition = models.ForeignKey(Conditions,verbose_name="the condition this set goes with",db_index=True,on_delete=models.CASCADE)
    category = models.ForeignKey(ActivitiesCategory,verbose_name="the category included in the set",db_index=True,on_delete=models.CASCADE)
    def __str__(self):
        return "ActivityCategorySet for Condition: "+str(self.condition)+" includes Category: "+str(self.category)

class ProgressiveUnlocking(models.Model):
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="the related course", db_index=True) # Remove this if using the instructor Id
    name = models.CharField(max_length=300) # e.g. test score, number of attempts 
    description = models.CharField(max_length=10000)
    ruleID = models.ForeignKey(Rules,  on_delete=models.SET_NULL, null=True, blank=True, verbose_name="the related rule", db_index=True)
    objectID = models.IntegerField(default=-1,verbose_name="index into the appropriate table") #ID of challenge,activity,etc. associated with a unlocking rule
    objectType = models.IntegerField(verbose_name="which type of object is involved, for example, challenge, individual question, or other activity.  Should be a reference to an objectType Enum", db_index=True,default=1301) # Defaulted to Challenges

