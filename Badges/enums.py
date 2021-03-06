# Function which takes a dictionary of dictionaries and converts them into a zipped list containing the specified fields.
def dict_dict_to_zipped_list(d,fields):
    output = []
    for key in d:
        attrlist = []
        for field in fields:
            attrlist.append(d[key][field])
        output.append(attrlist)
    return output
class Goal():
    warmup10 = 1600
    warmup70 = 1602
    warmup80 = 1604
    warmup90 = 1606
    streak10 = 1610
    streak70 = 1612
    streak80 = 1614
    streak90 = 1616
    courseBucks = 1620
    courseXP = 1630
    courseBadges = 1640
    goals = {
        warmup10:{
                'index': warmup10,
                'name': 'warmup10',
                'displayName': 'Number of Warm Ups to be taken',
                'description': 'The number of Warm Ups the student aims to take.',
                },
        warmup70:{
                'index': warmup70,
                'name': 'warmup70',
                'displayName': 'Number of Warm Ups taken with 70% score',
                'description': 'The number of Warm Ups the student aims to complete with a score of 70%',
                },
        warmup80:{
                'index': warmup80,
                'name': 'warmup80',
                'displayName': 'Number of Warm Ups to be taken with 80% score',
                'description': 'The number of Warm Ups the student aims to complete with a score of 80%.',
                },
        warmup90:{
                'index': warmup90,
                'name': 'warmup90',
                'displayName': 'Number of Warm Ups to be taken with 90% score',
                'description': 'The number of Warm Ups the student aims to complete with a score of 90%',
                },
        streak10:{
                'index': streak10,
                'name': 'streak10',
                'displayName': 'Number of consecutive days for Warm Ups',
                'description': 'The number consecutive days where at least one Warm Up is completed',
                },
        streak70:{
                'index': streak70,
                'name': 'streak70',
                'displayName': 'Number of consecutive days for Warm Ups with 70% score',
                'description': 'The number consecutive days where at least one Warm Up is completed with a score of 70%',
                },
        streak80:{
                'index': streak80,
                'name': 'streak80',
                'displayName': 'Number of consecutive days for Warm Ups with 80% score',
                'description': 'The number consecutive days where at least one Warm Up is completed with a score of 80%',
                },
        streak90:{
                'index': streak90,
                'name': 'streak90',
                'displayName': 'Number of consecutive days for Warm Ups with 90% score',
                'description': 'The number consecutive days where at least one Warm Up is completed with a score of 90%',
                },
        courseBucks:{
                'index': courseBucks,
                'name': 'courseBucks',
                'displayName': 'Number of Course Bucks earned',
                'description': 'The amount of Course Bucks earned',
                },
        courseXP:{
                'index': courseXP,
                'name': 'courseXP',
                'displayName': 'Amount of Course XP earned',
                'description': 'The amount of Course Experience Points earned by the student',
                },
        courseBadges:{
                'index': courseBadges,
                'name': 'courseBadges',
                'displayName': 'Number of Course Badges earned',
                'description': 'The number of Course Badges earned by the student',
                },
    }
    
class Action():
    giveBadge = 701 # Give a student a badge
    createNotification = 702 # Give a student a notification
    lock = 703 # Unknown.  In the fixture it said "When a student completes answering a particular question in a particular challenge"
    unlock = 704 # Unknown.  In the fixture it said "When an instructor enters some information for a particular activity"
    setValue = 705 # Change the value of a variable
    addSkillPoints = 706 # Add skill points
    unlockedProgressive = 707 # when a student is able to unlock a challenge activity or somethin else progressively
    
    increaseVirtualCurrency = 710 # Increases virtual currency (CourseBucks)
    decreaseVirtualCurrency = 711 # Decreases virtual currency (CourseBucks)

    completeGoal = 712 # Sends goal notification on completion
    DoApplause = 713 #displays virtual fireworks or confetti to the user
    
    actions = {
           giveBadge:{
                'index': giveBadge,
                'name': 'giveBadge',
                'displayName': 'Give Badge',
                'description': 'Give a student a badge',
                },   
           createNotification:{
                'index':createNotification,
                'name': 'createNotification',
                'displayName': 'Create Notification',
                'description': 'Give a student a notification'
                },
           lock:{
                'index':lock,
                'name': 'lock',
                'displayName': 'Lock?',
                'description': 'When a student completes answering a particular question in a particular challenge'
                },   
           unlock:{
                'index':unlock,
                'name': 'unlock',
                'displayName': 'Unlock?',
                'description': 'When an instructor enters some information for a particular activity'
                },
           setValue:{
                'index':setValue,
                'name': 'setValue',
                'displayName': 'Set Value',
                'description': 'Change the value of a variable'
                },
           addSkillPoints:{
                'index':addSkillPoints,
                'name': 'addSkillPoints',
                'displayName': 'Add Skill Points',
                'description': 'Add skill points'
                },
            unlockedProgressive:{
                'index':unlockedProgressive,
                'name': 'unlockedProgressive',
                'displayName': 'Unlocked Progressively',
                'description': 'When a student is able to unlock a challenge activity or somethin else progressively'
                },
           increaseVirtualCurrency:{
                'index':increaseVirtualCurrency,
                'name': 'increaseVirtualCurrency',
                'displayName': 'Increase Virtual Currency',
                'description': 'Increases Virtual Currency'
                },
            decreaseVirtualCurrency:{
                'index':decreaseVirtualCurrency,
                'name': 'decreaseVirtualCurrency',
                'displayName': 'Decrease Virtual Currency',
                'description': 'Decreases Virtual Currency'
                },
            completeGoal:{
                'index':completeGoal,
                'name': 'completeGoal',
                'displayName': 'Complete a Goal',
                'description': 'Sends notification that goal is completed and sets the goal status to completed'
            },
            DoApplause:{
                'index':DoApplause,
                'name': 'DoApplause',
                'displayName': 'do a applause',
                'description': 'displays virtual an Applause to the user'
            },
        }


class Event():
    #Challenge-Related Events
    #IMPLEMENTED
    startChallenge = 801 # When a student has started to attempt a particular challenge
    #IMPLEMENTED
    endChallenge = 802 # When a student has finished to attempt and has submitted a particular challenge
    
    #NOT IMPLEMENTED
    #The event trigger for this event cannot be implemented until the challenge-taking format
    #is changed to viewing only 1 question per page, rather than a long list of all questions
    completeQuestion = 803 # When a student completes answering a particular question in a particular challenge
    
    #IMPLEMENTED
    participationNoted = 804 # When an instructor acknowledges participation for a particular student for a particular activity
    #IMPLEMENTED
    #For timePassed event, consider distinguishing between timePassed for a entire challenge v.s. just a particular question
    timePassed = 805 # when the duration/time limit of a challenge has been reached
    
    #NOT IMPLEMENTED
    valueChanged = 806 # When the value of a particular variable in a particular challenge is changed
    
    #NOT IMPLEMENTED - implementation depends of the new version containing a question per page
    #The event trigger for this event cannot be implemented until the challenge-taking format
    #is changed to viewing only 1 question per page, rather than a long list of all questions
    startQuestion = 807 # When a student has started to attempt a particular question
    endQuestion = 808 # When a student has finished to attempt and has submitted a particular question
    
    #IMPLEMENTED
    userLogin = 809 # When a student logs in with their credentials
    
    #IMPLEMENTED in Instructors/challengeListView - when the instructor accesses the challenges list, the event is registered
    # to consider the entire class that has completed the challenge in mind. If this is done on the student's end, we would have
    # multiple unwanted event registers that would not work properly with some of the system variables
    challengeExpiration = 810 #When the time allowed for students to take a challenge expires.
    
    instructorAction = 811 #When Instructor awards points
    
    studentUpload = 812  #When a student uploads an assignment
    
    leaderboardUpdate = 813 #When the leaderboard gets updated
    
    spendingVirtualCurrency = 814  #When a student has spent VC
    
    visitedDashboard = 815   # Loaded the dashboard page.
    visitedEarnedVCpage = 816 # Student visited the Earning Virtual Currency Transaction page
    visitedSpendedVCpage = 817 # Student visited the Spended Virtual Currency Transaction page
    visitedBadgesInfoPage = 818  # Student visited the Badge info page
    visitedVCRulesInfoPage = 819  # Student visited the Virtual Currency Info info page
    visitedLeaderboardPage = 820 #Student visited leaderoard page
    clickedViewAverageGrade = 821 #student clicked view average grade on student achivements
    
    extendDeadlineHW = 851 # Extend the deadline of an assignment
    extendDeadlineLab = 852 # Extend the deadline of an assignment       
    instructorHelp = 853  # Get instructor help for an assignment
    buyAttempt = 854 # Buy another attempt for re-submission of an assignment
    buyExtraCreditPoints = 855 # Buy extra credit points for an assignment 
    replaceLowestAssignGrade = 856 # 
    buyTestTime = 857
    getDifferentProblem = 858 # Get a different dynamic problem on a test
    getCreditForOneTestProblem = 859 #
    getSurpriseAward = 860 # Get a small surprise award from the instructor   
    changeHWWeights = 862 # Set weights on the grades of 2 HWs
    examExemption = 863 # Get Exempt from Final
    buyMissedLab = 864  # Buy the points for a missed lab
    
    adjustment = 861
#    seeClassAverage = 861 # See aggregated class information
#    chooseLabPartner = 862 # Choose a lab partner
#    chooseProjectPartner = 863 # Choose a project partner
#    uploadOwnAvatar = 864 # Upload own avatar
#    chooseDashboardBackground = 865 # Choose a background for the student dashboard
#    chooseBackgroundForYourName = 866 # ?
    
    classAttendance = 870
    activitySubmission = 871

    #             #              #
    # Challenge Classmates Events#
   
    # Duel 
    duelSent = 872
    duelAccepted = 873
    duelWon = 874
    duelLost = 875

    # Call Outs
    calloutSent = 876
    calloutRequested = 877
    calloutWon = 878
    calloutLost = 879
    #             #              #
    # TODO: Rearrange enums into categories
    virtualCurrencyEarned = 880
    badgeEarned = 881

    levelUp = 882
    #flashcard
    viewFlashCard = 883
    submitFlashCard = 884
    
    doVirtualApplause = 885
    


    events = {
              startChallenge: {
                        'index': startChallenge,
                        'name':'startChallenge',
                        'displayName':'Start of Challenge',
                        'description':'Time when a student has started to attempt a particular challenge',
                        'isVirtualCurrencySpendRule':False
                        },
              endChallenge: {
                        'index': endChallenge,
                        'name':'endChallenge',
                        'displayName':'End of Challenge',
                        'description':'Time when a student has finished to attempt and has submitted a particular challenge',
                        'isVirtualCurrencySpendRule':False
                        },
              completeQuestion: {
                        'index': completeQuestion,
                        'name':'completeQuestion',
                        'displayName':'Question Completed',
                        'description':'A student completes answering a particular question in a particular challenge',
                        'isVirtualCurrencySpendRule':False
                        },
              participationNoted: {
                        'index': participationNoted,
                        'name':'participationNoted',
                        'displayName':'Instructor Notes Participation',
                        'description':'An instructor acknowledges participation for a particular student for a particular activity',
                        'isVirtualCurrencySpendRule':False
                        },
              instructorAction: {
                        'index': instructorAction,
                        'name':'instructorAction',
                        'displayName':'Instructor Action',
                        'description':'An instructor awards points for a particular activity',
                        'isVirtualCurrencySpendRule':False
                        },
              classAttendance: {
                        'index': classAttendance,
                        'name':'classAttendance',
                        'displayName':'Instructor set student attendance',
                        'description':'An instructor enters class attendance for a particular student on a particular date',
                        'isVirtualCurrencySpendRule':False
                        },              
              timePassed: {
                        'index': timePassed,
                        'name':'timePassed',
                        'displayName':'Time Passed',
                        'description':'The duration/time limit of a challenge has been reached',
                        'isVirtualCurrencySpendRule':False
                        },
              valueChanged: {
                        'index': valueChanged,
                        'name':'valueChanged',
                        'displayName':'Variable Changes Value',
                        'description':'The value of a particular variable in a particular challenge is changed',
                        'isVirtualCurrencySpendRule':False
                        },
              startQuestion: {
                        'index': startQuestion,
                        'name':'startQuestion',
                        'displayName':'Start of Question',
                        'description':'Time when a student has started to attempt a particular question',
                        'isVirtualCurrencySpendRule':False
                        },
              endQuestion: {
                        'index': endQuestion,
                        'name':'endQuestion',
                        'displayName':'End of Question',
                        'description':'Time when a student has finished to attempt and has submitted a particular question',
                        'isVirtualCurrencySpendRule':False
                        },
              studentUpload: {
                        'index': studentUpload,
                        'name':'studentUpload',
                        'displayName':'Student Uploads Assignment',
                        'description':'A student uploads an assignment',
                        'isVirtualCurrencySpendRule':False
                        },
              leaderboardUpdate: {
                        'index': leaderboardUpdate,
                        'name':'leaderboardUpdate',
                        'displayName':'The Leaderboard is Updated',
                        'description':'The leaderboard is updated',
                        'isVirtualCurrencySpendRule':False
                        },

              userLogin: {
                        'index': userLogin,
                        'name':'userLogin',
                        'displayName':'User Login',
                        'description':'A student logs in with their credentials',
                        'isVirtualCurrencySpendRule':False
                          },
              challengeExpiration: {
                        'index': challengeExpiration,
                        'name':'challengeExpiration',
                        'displayName':'Challenge Expiration',
                        'description':'The time allowed for students to take a challenge expires.',
                        'isVirtualCurrencySpendRule':False
                        },
              spendingVirtualCurrency: {
                        'index': spendingVirtualCurrency,
                        'name': 'spendingVirtualCurrency',
                        'displayName': 'Spending Virtual Currency',
                        'description': 'A student has spent virtual currency',
                        'isVirtualCurrencySpendRule': True,
                        },
              visitedDashboard: {
                        'index': visitedDashboard,
                        'name': 'visitedDashboard',
                        'displayName': 'Visited Dashboard',
                        'description': 'Loaded the dashboard page',
                        'isVirtualCurrencySpendRule':False
                        },
              visitedEarnedVCpage: {
                        'index': visitedEarnedVCpage,
                        'name': 'visitedEarnedVCpage',
                        'displayName': 'Visited Earning Transactions page',
                        'description': 'Student visited the earning virtual currency transactions page',
                        'isVirtualCurrencySpendRule':False
                        },
              visitedSpendedVCpage: {
                        'index': visitedSpendedVCpage,
                        'name': 'visitedSpendedVCpage',
                        'displayName': 'Visited Spending Transactions page',
                        'description': 'Student visited the spending virtual currency transactions page',
                        'isVirtualCurrencySpendRule':False
                        },
              visitedBadgesInfoPage: {
                        'index': visitedBadgesInfoPage,
                        'name': 'visitedBadgesInfoPage',
                        'displayName': 'Visited Badges Info page',
                        'description': 'Student visited the Badges info page',
                        'isVirtualCurrencySpendRule':False
                        },
              visitedVCRulesInfoPage: {
                        'index': visitedVCRulesInfoPage,
                        'name': 'visitedVCRulesInfoPage',
                        'displayName': 'Visited VC Rules Info page',
                        'description': 'Student visited the virtual currency rules info page',
                        'isVirtualCurrencySpendRule':False
                        },
              
              visitedLeaderboardPage: {
                        'index': visitedLeaderboardPage,
                        'name': 'visitedLeaderboardPage',
                        'displayName': 'Visited class leaderboard page',
                        'description': 'Student visited the class leaderboard page',
                        'isVirtualCurrencySpendRule':False
                        },
            clickedViewAverageGrade: {
                        'index': clickedViewAverageGrade,
                        'name': 'clickedViewAverageGrade',
                        'displayName': 'Student clicked on display average grade button',
                        'description': 'Student clicked on display average grade button',
                        'isVirtualCurrencySpendRule':False
                        },
             
              instructorHelp: {
                        'index': instructorHelp,
                        'name':'instructorHelp',
                        'displayName':'Get Help on 1 HW Problem',
                        'description':'Get help/feedback from the instructor on 1 problem before submitting an assignment.',
                        'isVirtualCurrencySpendRule':True
                        },
              buyAttempt: {
                        'index': buyAttempt,
                        'name':'buyAttempt',
                        'displayName':'Buy HW Re-submission',
                        'description':'Buy another attempt (re-submission) for an assignment (restrictions may apply).',
                        'isVirtualCurrencySpendRule':True
                        },
              extendDeadlineHW: {
                        'index': extendDeadlineHW,
                        'name':'extendDeadlineHW',
                        'displayName':'Extend HW Deadline',
                        'description':'Extend the due date for an assignment with 12 hours.',
                        'isVirtualCurrencySpendRule':True
                        },              
              extendDeadlineLab: {
                        'index': extendDeadlineLab,
                        'name':'extendDeadlineLab',
                        'displayName':'Extend Deadline of Lab',
                        'description':'Extend the due date for a lab with 24 hours.',
                        'isVirtualCurrencySpendRule':True
                        },              
              buyExtraCreditPoints: {
                        'index': buyExtraCreditPoints,
                        'name':'buyExtraCreditPoints',
                        'displayName':'Buy Extra Credit Points',
                        'description':'Buy 5 extra credit points for an assignment.',
                        'isVirtualCurrencySpendRule':True
                        },
              replaceLowestAssignGrade: {
                        'index': replaceLowestAssignGrade,
                        'name':'replaceLowestAssignGrade',
                        'displayName':'Replace Lowest HW Grade',
                        'description':'Replace your lowest assignment grade with your average assignment grade.',
                        'isVirtualCurrencySpendRule':True
                        },              
              buyTestTime: {
                        'index': buyTestTime,
                        'name':'buyTestTime',
                        'displayName':'Buy Test Time',
                        'description':'Buy a 15-min extension of the time for one test.',
                        'isVirtualCurrencySpendRule':True
                        }, 
              buyMissedLab: {
                        'index': buyMissedLab,
                        'name':'buyMissedLab',
                        'displayName':'Buy Missed Lab',
                        'description':'Buy the points for a missed lab.',
                        'isVirtualCurrencySpendRule':True
                        },                                         
              getDifferentProblem: {
                        'index': getDifferentProblem,
                        'name':'getDifferentProblem',
                        'displayName':'Get Different Test Problem',
                        'description':'Get 1 different problem on a test (for designated problems).',
                        'isVirtualCurrencySpendRule':True
                        },              
              getCreditForOneTestProblem: {
                        'index': getCreditForOneTestProblem,
                        'name':'getCreditForOneTestProblem',
                        'displayName':'Get Credit for One Test Problem',
                        'description':'Get full credit for 1 problem (from designated problems) in 1 test.',
                        'isVirtualCurrencySpendRule':True
                        },              
              getSurpriseAward: {
                        'index': getSurpriseAward,
                        'name':'getSurpriseAward',
                        'displayName':'Get Surprise Award',
                        'description':'Get a small surprise award from the instructor.',
                        'isVirtualCurrencySpendRule':True
                        },
              changeHWWeights: {
                        'index': changeHWWeights,
                        'name':'changeHWWeights',
                        'displayName':'Change HW Weights',
                        'description':'Set weights on the grades of 2 HWs. The weights must total 200%, with each weight between 75% and 125%.',
                        'isVirtualCurrencySpendRule':True
                        },
              examExemption: {
                        'index': examExemption,
                        'name':'examExemption',
                        'displayName':'Get Exempt from Final',
                        'description':'If you have accumulated 700+ course points, you can buy an exemption from the Final exam.',
                        'isVirtualCurrencySpendRule':True
                        },
              adjustment: {
                        'index': adjustment,
                        'name':'adjustment',
                        'displayName':'adjustment',
                        'description':'when teacher adjust a student challenge grade.',
                        'isVirtualCurrencySpendRule':False
                        },
              activitySubmission: {
                        'index': activitySubmission,
                        'name':'activitySubmission',
                        'displayName':'activitySubmission',
                        'description':'when a student submits an activity',
                        'isVirtualCurrencySpendRule':True
                        },
            duelSent: {
                        'index': duelSent,
                        'name':'duelSent',
                        'displayName':'duelSent',
                        'description':'when a student sent a duel',
                        'isVirtualCurrencySpendRule':False
                        },
            duelAccepted: {
                        'index': duelAccepted,
                        'name':'duelAccepted',
                        'displayName':'duelAccepted',
                        'description':'when a student accepted a duel',
                        'isVirtualCurrencySpendRule':False
                        },
            duelWon: {
                        'index': duelWon,
                        'name':'duelWon',
                        'displayName':'duelWon',
                        'description':'when a student wins a duel',
                        'isVirtualCurrencySpendRule':False
                        },
            duelLost: {
                        'index': duelLost,
                        'name':'duelLost',
                        'displayName':'duelLost',
                        'description':'when a student lose a duel',
                        'isVirtualCurrencySpendRule':False
                        },
            calloutSent: {
                        'index': calloutSent,
                        'name':'calloutSent',
                        'displayName':'calloutSent',
                        'description':'when a student sends a call out',
                        'isVirtualCurrencySpendRule':False
                        },
            calloutRequested: {
                        'index': calloutRequested,
                        'name':'calloutRequested',
                        'displayName':'calloutRequested',
                        'description':'when a student get requested a call out',
                        'isVirtualCurrencySpendRule':False
                        },
            calloutWon: {
                        'index': calloutWon,
                        'name':'calloutWon',
                        'displayName':'calloutWon',
                        'description':'when a student wins a call out',
                        'isVirtualCurrencySpendRule':False
                        },
            calloutLost: {
                        'index': calloutLost,
                        'name':'calloutLost',
                        'displayName':'calloutLost',
                        'description':'when a student loses a call out',
                        'isVirtualCurrencySpendRule':False
                        },
            virtualCurrencyEarned: {
                        'index': virtualCurrencyEarned,
                        'name':'virtualCurrencyEarned',
                        'displayName':'Student earned Virtual Currency',
                        'description':'Event triggered when a student has earned a virtual currency',
                        'isVirtualCurrencySpendRule':False
                        },
            badgeEarned: {
                        'index': badgeEarned,
                        'name':'badgeEarned',
                        'displayName':'Student earned a Badge',
                        'description':'Event triggered when a student has earned a badge',
                        'isVirtualCurrencySpendRule':False
                        },
            viewFlashCard: {
                        'index': viewFlashCard,
                        'name':'viewFlashCard',
                        'displayName':'Student viewed a flash card',
                        'description':'Event triggered when students starts a flash card',
                        'isVirtualCurrencySpendRule':False
                        },
            submitFlashCard: {
                        'index': submitFlashCard,
                        'name':'submitFlashCard',
                        'displayName':'Student finished a flash card',
                        'description':'Event triggered when a student finishes flash card',
                        'isVirtualCurrencySpendRule':False
                        },
       
#               seeClassAverage: {
#                         'index': seeClassAverage,
#                         'name':'seeClassAverage',
#                         'displayName':'See Class Average',
#                         'description':'See aggregated class information',
#                         'isVirtualCurrencySpendRule':True
#                         },  
#               chooseLabPartner: {
#                         'index': chooseLabPartner,
#                         'name':'chooseLabPartner',
#                         'displayName':'Choose Lab Partner',
#                         'description':'Choose a lab partner',
#                         'isVirtualCurrencySpendRule':True
#                         },                            
#               chooseProjectPartner: {
#                         'index': chooseProjectPartner,
#                         'name':'chooseProjectPartner',
#                         'displayName':'Choose Project Partner',
#                         'description':'Choose a project partner',
#                         'isVirtualCurrencySpendRule':True
#                         },                            
#               uploadOwnAvatar: {
#                         'index': uploadOwnAvatar,
#                         'name':'uploadOwnAvatar',
#                         'displayName':'Upload Own Avatar',
#                         'description':'Upload your own avatar.',
#                         'isVirtualCurrencySpendRule':True
#                         },
#               chooseDashboardBackground: {
#                         'index': chooseDashboardBackground,
#                         'name':'chooseDashboardBackground',
#                         'displayName':'Choose Dashboard Background',
#                         'description':'Choose a background for the your dashboard',
#                         'isVirtualCurrencySpendRule':True
#                         },
#               chooseBackgroundForYourName: {
#                         'index': chooseBackgroundForYourName,
#                         'name':'chooseBackgroundForYourName',
#                         'displayName':'Choose Background for Your Name',
#                         'description':'Choose background or border for your name',
#                         'isVirtualCurrencySpendRule':True
#                         },              

              }

class displayCircumstance():
    badges = 9301
    virtualCurrency = 9302

system_variable_type_to_HTML_type = {
    "string":"text",
    "date":"date",
    "int":"number",
    "boolean":"checkbox"
}

class ObjectTypes():
    challenge=1301
    activity=1302
    question=1303
    form=1304 # Used in the case of handling general form submits (user login, etc.)
    none=1305 # Not an actual object, but used to indicate that a variable only makes sense in the global context
                # rather than the context of any particular object in circumstances where that is needed.
    topic=1306
    activityCategory=1307
    virtualCurrencySpendRule=1308 # Used for manual virtual currency rules/transactions
    flashcard = 1309
    skill = 1310
    objectTypes = {
        challenge:"challenge",
        activity:"activity",
        question:"question",
        form:"form",
        none:"global", # We would actually have called this "global" to begin with, but it's a reserved word.
        topic:"topic",
        activityCategory:"activityCategory",
        virtualCurrencySpendRule:"virtualCurrencySpendRule",
        flashcard:"flashcard",
        skill:"skill",
    }

class OperandTypes():
    immediateInteger=1001
    condition=1002
    floatConstant=1003
    stringConstant=1004
    systemVariable=1005
    challengeSet=1006
    activitySet=1007
    conditionSet=1008
    boolean=1009
    dateConstant=1010
    noOperand=1011
    topicSet=1012
    activtiyCategorySet = 1013
    skillSet = 1014
    operandTypes={
        immediateInteger:'immediateInteger',
        condition:'condition',
        floatConstant:'floatConstant',
        stringConstant:'stringConstant',
        systemVariable:'systemVariable',
        challengeSet:'challengeSet',
        activtiyCategorySet:'activtiyCategorySet',
        activitySet:'activitySet',
        conditionSet:'conditionSet',
        boolean:'boolean',
    }

class AwardFrequency:
    justOnce = 1100
    perChallenge = 1101
    perActivity = 1102
    # PerTopic, daily, and weekly are commented out because the work to support it right now is too much for the available time.
    # It's not bad in general, but removed until I have time to do the work -KI
    perTopic = 1103
    #daily = 1104
    #weekly = 1105
    perActivityCategory = 1106
    awardFrequency = {
        justOnce:{
            'index': justOnce,
            'name': 'Just Once Ever',
            'objectType': ObjectTypes.none,
            'objectTypeName': 'none',
        },
        perChallenge:{
            'index': perChallenge,
            'name': 'Once per Challenge',
            'objectType': ObjectTypes.challenge,
            'objectTypeName': 'challenge',

        },
        perActivity:{
            'index': perActivity,
            'name': 'Once per Activity',
            'objectType': ObjectTypes.activity,
            'objectTypeName': 'activity',
        },
        perTopic:{
            'index': perTopic,
            'name': 'Once per Topic',
            'objectType': ObjectTypes.topic,
            'objectTypeName': 'topic',
        },
        #daily:{
        #    'index': daily,
        #    'name': 'Once per day',
        #},
        #weekly:{
        #    'index': weekly,
        #    'name': 'Once per day',
        #},
        perActivityCategory:{
            'index':perActivityCategory,
            'name': 'Once per Category',
            'objectType': ObjectTypes.activityCategory,
            'objectTypeName': 'activityCategory',
        },
    }
    
class ApplauseOption:
    random = 1200
    fireworks = 1201
    confetti = 1202
    
    applauseOption = {
        random:{
            'index': random,
            'name': 'Random',
            'objectType': ObjectTypes.none,
            'objectTypeName': 'none',
            "jslaunchCode":"""var ind = Math.floor( Math.random() * 2 );                         
                            switch(ind){
                                case 0:{ doFireworks() } break;
                                case 1:{ doConfetti()  } break;
                            }"""
        },
        fireworks:{
            'index': fireworks,
            'name': 'Fireworks',
            'objectType': ObjectTypes.none,
            'objectTypeName': 'none',
            "jslaunchCode": "doFireworks(); "
        },
        confetti:{
            'index': confetti,
            'name': 'Confetti',
            'objectType': ObjectTypes.none,
            'objectTypeName': 'none',
            "jslaunchCode": "doConfetti(); "

        },
    }
  
class GoalFlag():
    isStudentGoal = 'studentGoal'
    requireBadgesEnabled = 'badgesUsed'
    requireTeamsEEnabled = 'teamsEnabled'
    requireAdaptationUEnabled = 'adaptationUsed'
    requireWarmupsEnabled = 'warmupsUsed'
    requireFlashcardsEnabled = 'flashcardsUsed'
    requireActivitiesEnabled = 'activitiesUsed'
    requireSkillsEnabled = 'skillsUsed',
    requireLevelingEnabled = 'levelingUsed'
    
    def values(self):
        return ['studentGoal', 'badgesUsed', 'teamsEnabled', 'adaptationUsed', 'warmupsUsed', 'flashcardsUsed', 'activitiesUsed', 'skillsUsed', 'levelingUsed']

