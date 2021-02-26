from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from django_celery_beat.models import PeriodicTask

from Badges.enums import Action, AwardFrequency, Event, OperandTypes
from Badges.systemVariables import SystemVariable
from Instructors.models import (Activities, ActivitiesCategory, Challenges,
                                Courses, Skills, Topics)


def custom_now():
    return now().replace(microsecond=0)


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
    ruleID = models.ForeignKey(Rules,  on_delete=models.SET_NULL, null=True, blank=True, verbose_name="the related rule", db_index=True)

    def __str__(self):              
        return "Badge#"+str(self.badgeID)+":"+str(self.badgeName)    

# Table for Periodic Badges
class PeriodicBadges(BadgesInfo):
    periodicVariableID = models.IntegerField() # The Perioidc Variable index set for this badge
    timePeriodID = models.IntegerField() # The Time Period index set for this badge
    periodicType = models.IntegerField(default=0) # The type of selected: TopN (0), All(1), Random(2)
    numberOfAwards = models.IntegerField(default=1, null=True) # The top number of students to award this badge to
    threshold = models.CharField(default="1", max_length=3) # The cutoff number of the result of the periodic variable function 
    operatorType = models.CharField(default='=', max_length=2) # The operator for the threshold (>=, >, =)
    isRandom = models.NullBooleanField(default=False) # Is this being awarded to random student(s)
    lastModified = models.DateTimeField(default=custom_now) # The last time this rule was modified. Used to properly calculate periodic variables when first starting
    periodicTask = models.ForeignKey(PeriodicTask,  null=True, blank=True, on_delete=models.SET_NULL, verbose_name="the periodic task", db_index=True) # The celery Periodic Task object
    resetStreak = models.BooleanField(default = False)
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
    vcAmountVaries = models.BooleanField(default=False) #for manual-rule checkbox
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
    threshold = models.CharField(default="1", max_length=3) # The cutoff number of the result of the periodic variable function 
    operatorType = models.CharField(default='=', max_length=2) # The operator for the threshold (>=, >, =)
    isRandom = models.NullBooleanField(default=False) # Is this being awarded to random student(s)
    lastModified = models.DateTimeField(default=custom_now) # The last time this rule was modified. Used to properly calculate periodic variables when first starting
    periodicTask = models.ForeignKey(PeriodicTask, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="the periodic task", db_index=True) # The celery Periodic Task object
    resetStreak = models.BooleanField(default = False)
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
    lastModified = models.DateTimeField(default=custom_now) # The last time this rule was modified. Used to properly calculate periodic variables when first starting
    periodicTask = models.ForeignKey(PeriodicTask,  null=True, blank=True, on_delete=models.SET_NULL, verbose_name="the periodic task", db_index=True) # The celery Periodic Task object
    howFarBack = models.IntegerField(default=0000)
    def delete(self, *args, **kwargs):
        ''' Custom delete method which deletes the PeriodicTask object before deleting the leaderboard config.'''
        if self.periodicTask != None:
            self.periodicTask.delete()
        super().delete(*args, **kwargs)

    def __str__(self):              
        return "Leaderboard#"+str(self.leaderboardID)+":"+str(self.leaderboardName)   

   
class CourseConfigParams(models.Model):
    ccpID = models.AutoField(primary_key=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="the related course", db_index=True)

    gamificationUsed = models.BooleanField(default=False) 
    courseAvailable = models.BooleanField(default=False)               ## Is the course open or closed?
    badgesUsed = models.BooleanField(default=False)                   ## The badgesUsed is for instructor dashboard purposes and system uses as well
    studCanChangeBadgeVis = models.BooleanField(default=False)        ## The studCanChangeBadgeVis is for allowing student to configure student dashboard visibility only
    numBadgesDisplayed = models.IntegerField(default=0)               ## This is used to display the number of students in the leaderboard dashboard html table

    levelingUsed = models.BooleanField(default=False)                 ##
    levelTo1XP = models.DecimalField(decimal_places=2, max_digits=100, default=10)
    nextLevelPercent = models.DecimalField(decimal_places=2, max_digits=100, default=50)
    
    # Duels related
    classmatesChallenges = models.BooleanField(default=False)         ## This is used for duels and call-outs
    betVC = models.BooleanField(default=False)                        ## Allow the bet of virtual currency in duels
    vcDuelParticipants = models.IntegerField(default=0)               ## Amount of virtual currency rewarded to duel participants
    vcDuel = models.IntegerField(default=0)                           ## Amount of virtual currency rewarded to duel winners
    vcDuelMaxBet = models.IntegerField(default=3)                     ## Max Amount of betting virtual currency 
    vcCallout = models.IntegerField(default=0)                        ## Amount of virtual currency rewarded to call-outs participants
    calloutAfterWarmup = models.BooleanField(default=False)           ## Allow students to callout other students after correctly solve a warm up 
    minimumCreditPercentage = models.IntegerField(default=0)          ## Instructor may set the minimum score percentage that must be reached for a student to get credit for the duel

    # Progress bar
    progressBarUsed = models.BooleanField(default=False)               ## This is the progress bar in the student achievements page and student course home page
    progressBarTotalPoints = models.IntegerField(default=100)         ## This is the default maximum points on the progress bar
    progressBarGroupUsed = models.BooleanField(default=False)          ## This will make the progress bar show data for the class instead of a student
    progressBarGroupAverage = models.BooleanField(default=True)       ## When the group progress bar is enabled, this will calculate the class values as a sum (total) or average

    displayStudentStartPageSummary = models.BooleanField(default=False) ## This toggles the view on the student course home page to show class achievements or student achievements summary

    displayAchievementPage = models.BooleanField(default=False)       ## This toggles the view on the student achievement page in the nav bars

    chatUsed = models.BooleanField(default=False)                      ## This will enable or disable the chat feature 
    
    seriousChallengesGrouped = models.BooleanField(default=False)     ## Show the serious challenges grouped by topics similar to warmup challenges on the instructor side

    leaderboardUsed = models.BooleanField(default=False)              ##
    studCanChangeLeaderboardVis = models.BooleanField(default=False)  ##
    numStudentsDisplayed = models.IntegerField(default=0)             ## This is used to display the number of studentss in the leaderboard dashboard html table

    classSkillsDisplayed = models.BooleanField(default=False)         ## The classSkillsDisplayed is only for dashboard purposes for the instructor
    studCanChangeClassSkillsVis = models.BooleanField(default=False)  ## The classSkillsDisplayed is only for dashboard purposes for the student
    numStudentBestSkillsDisplayed = models.IntegerField(default=0)    ## This is used to display the number of students in the Skills dashboard html table

    
    contentUnlockingDisplayed  = models.BooleanField(default=False)         ## The contentUnlockingDisplayed is only for displaying in menu for the instructor
    debugSystemVariablesDisplayed  = models.BooleanField(default=False) ## The debugSystemVariablesDisplayed is only for displaying in menu for the instructor
    
    ## Other fields for rule based configurations
    virtualCurrencyUsed = models.BooleanField(default=False)          ## isCourseBucksDisplayed was renamed, this is used in individual achievements
    virtualCurrencyAdded = models.IntegerField(default=0)             # Amount of course bucks given by the instructor to all students
    avatarUsed = models.BooleanField(default=False)                   ## This is to allow the student to upload an avatar.
    classAverageUsed = models.BooleanField(default=False)             ## ranga used this, in individual achievements
    studCanChangeclassAverageVis = models.BooleanField(default=False) ## The student can suppress visibility in the dashboard

    ##Misc Leaderboard Fields
    courseStartDate=models.DateField(default=custom_now)            ##
    courseEndDate=models.DateField(default=custom_now)              ##

    hasCourseStartDate = models.BooleanField(default=False) # Flags used to determine if the timestamp should be used or not
    hasCourseEndDate = models.BooleanField(default=False)

    leaderboardUpdateFreq=models.IntegerField(default=1)
    skillLeaderboardDisplayed = models.BooleanField(default=False)         ## Frequency in days, minimum 1 and maximum 365 days
    customLeaderboardsUsed = models.BooleanField(default=False)

    ##XP Weights CalcualtionFields
    xpWeightSP = models.IntegerField(default=0)                       ## XP Weights for Skill Points
    xpWeightSChallenge = models.IntegerField(default=0)               ## XP Weights for Serious Challenges
    xpWeightWChallenge = models.IntegerField(default=0)               ## XP Weights for Warm up Challenges
    xpWeightAPoints    = models.IntegerField(default=0)               ## XP Weights for Activity Points

    xpCalculateSeriousByMaxScore = models.BooleanField(default=False) ## This will decide how to calculate xp for serious challenges: either by 
                                                                      ## max score of scores or by the first attempt score
    xpCalculateWarmupByMaxScore = models.BooleanField(default=True)  ## Same as preivous but for warmup challenges

    ## Levels of Difficulties for the course
    thresholdToLevelMedium = models.IntegerField(default=0)           ## Thresholds in %  of previous level for moving from Easy (default level) to Medium
    thresholdToLevelDifficulty = models.IntegerField(default=0)       ## Thresholds in %  of previous level for moving from Medium (default level) to Hard
    
    streaksUsed = models.BooleanField(default = False)                 ##
    
    ## Student Goal Setting
    goalsUsed = models.BooleanField(default=False)                    ## Enables the use of goal setting for students
    studCanChangeGoal = models.BooleanField(default=False)             ## Allows student to change the visibility of goals component

    #Options to disable Warmups, Serious Challenges, FlashCards, and the Gradebook
    warmupsUsed = models.BooleanField(default=True)
    seriousChallengesUsed = models.BooleanField(default=True)
    gradebookUsed = models.BooleanField(default=False)
    flashcardsUsed = models.BooleanField(default=False)
    #Options to disable activities, skills, and announcements
    activitiesUsed = models.BooleanField(default=False)  
    skillsUsed = models.BooleanField(default=False)
    announcementsUsed = models.BooleanField(default=False)

    #hints system
    hintsUsed = models.BooleanField(default = False)
    weightBasicHint = models.IntegerField(default=0)     ##  Costs as a percentage of points lost for accepting the hint.
    weightStrongHint = models.IntegerField(default=0) ##     

    #Teams system
    teamsLockInDeadline = models.DateTimeField(default=custom_now, verbose_name='Deadline for team members to be locked in to the team') ##Deadline for students to join a team
    maxNumberOfTeamStudents = models.IntegerField(default=3)   ##maximum number of team students allowed per team
    teamsEnabled = models.BooleanField(default = False) ##teams enabled for the course
    selfAssignment = models.BooleanField(default = True, verbose_name='Students can auto-assign themselves to teams') ##allow student self-assignment to teams
    def __str__(self):
        return "id:"+str(self.ccpID)  +", course:"+str(self.courseID) +", badges:"+str(self.badgesUsed) +",studcanchangebadgevis:" \
        +str(self.studCanChangeBadgeVis) +"," \
        +str(self.numBadgesDisplayed) +"," \
        +str(self.levelingUsed) +"," \
        +str(self.classmatesChallenges) +"," \
        +str(self.vcDuel) +"," \
        +str(self.vcCallout) +"," \
        +str(self.progressBarUsed) +"," \
        +str(self.chatUsed) +"," \
        +str(self.seriousChallengesGrouped) +"," \
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
        +str(self.xpWeightAPoints) +"," \
        +str(self.xpCalculateSeriousByMaxScore)+"," \
        +str(self.xpCalculateWarmupByMaxScore)+"," \
        +str(self.classmatesChallenges)+","\
        +str(self.betVC)+","\
        +str(self.vcCallout)+","\
        +str(self.vcDuel)+","\
        +str(self.vcDuelMaxBet)+","\
        +str(self.vcDuelParticipants)+","\
        +str(self.studCanChangeGoal)+","\
        +str(self.warmupsUsed)+","\
        +str(self.seriousChallengesUsed)+","\
        +str(self.gradebookUsed)+","\
        +str(self.activitiesUsed)+","\
        +str(self.skillsUsed)+","\
        +str(self.announcementsUsed)+","\
        +str(self.hintsUsed)+","\
        +str(self.weightBasicHint)+","\
        +str(self.weightStrongHint)+","\
        +str(self.teamsLockInDeadline)+","\
        +str(self.maxNumberOfTeamStudents)+","\
        +str(self.teamsEnabled)+","\
        +str(self.selfAssignment)
 
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
    
class SkillSet(models.Model):
    condition = models.ForeignKey(Conditions,verbose_name="the condition this set goes with",db_index=True,on_delete=models.CASCADE)
    skill = models.ForeignKey(Skills,verbose_name="the skill included in the set",db_index=True,on_delete=models.CASCADE)
    def __str__(self):
        return "SkillSet for Condition: "+str(self.condition)+" includes Skill: "+str(self.skill)

class ProgressiveUnlocking(models.Model):
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="the related course", db_index=True) # Remove this if using the instructor Id
    name = models.CharField(max_length=300) # e.g. test score, number of attempts 
    description = models.CharField(max_length=10000)
    ruleID = models.ForeignKey(Rules,  on_delete=models.SET_NULL, null=True, blank=True, verbose_name="the related rule", db_index=True)
    objectID = models.IntegerField(default=-1,verbose_name="index into the appropriate table") #ID of challenge,activity,etc. associated with a unlocking rule
    objectType = models.IntegerField(verbose_name="which type of object is involved, for example, challenge, individual question, or other activity.  Should be a reference to an objectType Enum", db_index=True,default=1301) # Defaulted to Challenges

class AttendanceStreakConfiguration(models.Model):
    streakConfigurationID = models.AutoField(primary_key=True)
    courseID = models.ForeignKey(Courses, on_delete=models.SET_NULL, null=True,verbose_name="the related course", db_index=True) 
    daysofClass = models.CharField(max_length=75)#days of the week that are class scheduled for semester
    daysDeselected = models.CharField(max_length=20000)#the days that were removed from the class schedule
    def __str__(self):              
        return str(self.streakConfigurationID)+","+str(self.courseID)+","+str(self.daysofClass) +","+ str(self.daysDeselected)


# Table for logging who added what to who
class BadgesVCLog(models.Model):
    badgesVCLogID = models.AutoField(primary_key=True)
    courseID = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="the related course", db_index=True)
    log_data = models.TextField(blank=True, default='{}', verbose_name='Log Data',
            help_text='JSON encoded data (Example: {"badge": {"name": "badge name", "type": "automatic, manual, periodic"},})')
    timestamp = models.DateTimeField(default=custom_now, blank=True)#when it was issued
    def __str__(self):              
        return f"ID: {self.badgesVCLogID} : Course: {self.courseID} : Data: {self.log_data}"

class CeleryTaskLog(models.Model):
    ''' Log of ran celery tasks (as of now periodic ones) that can be used to check
        if the celery task did not run at its time period
    '''
    celeryTaskLogID = models.AutoField(primary_key=True)
    taskID = models.CharField(max_length=200, unique=True, verbose_name='Task ID',
            help_text='The Unique Task ID. (Example: "unique_warmups_123_badge")')
    parameters = models.TextField(blank=True, default='{}', verbose_name='Task Parameters',
            help_text='JSON encoded keyword arguments of celery parameters. (Example: {"argument": "value"})')
    timestamp = models.DateTimeField(default=custom_now, verbose_name='Task Timestamp',
            help_text='The last time the celery task has run completely and was recorded')
    def __str__(self):
        return "Task ID: {} - Updated: {}".format(self.taskID, self.timestamp)
    
class CeleryTestResult(models.Model):
    uniqid= models.CharField(max_length=200)
    sequence = models.IntegerField()
    def __str__(self):
        return "Test "+self.sequence+":"+self.uniqid
