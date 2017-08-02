# Function which takes a dictionary of dictionaries and converts them into a zipped list containing the specified fields.
def dict_dict_to_zipped_list(d,fields):
    output = []
    for key in d:
        attrlist = []
        for field in fields:
            attrlist.append(d[key][field])
        output.append(attrlist)
    return output

class Action():
    giveBadge = 701 # Give a student a badge
    createNotification = 702 # Give a student a notification
    lock = 703 # Unknown.  In the fixture it said "When a student completes answering a particular question in a particular challenge"
    unlock = 704 # Unknown.  In the fixture it said "When an instructor enters some information for a particular activity"
    setValue = 705 # Change the value of a variable
    addSkillPoints = 706 # Add skill points
    
    increaseVirtualCurrency = 710 # Increases virtual currency (CourseBucks)
    decreaseVirtualCurrency = 711 # Decreases virtual currency (CourseBucks)
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
    
    buyHint = 850  #Buy one hint for an assignment
    buyAttempt = 851 #Buy a permission for one re-submission of an assignment
    extendDeadline = 852 #Extend the deadline of an assignment with 12 hours 
    dropLowestAssignGrade = 853 #Drop the lowest assignment grade
    getDifferentProblem = 854 #Get a different dynamic problem on a test
    seeClassAverage = 855 #See aggregated class information
    chooseLabPartner = 856 #Choose a lab partner
    chooseProjectPartner = 857 #Choose a project partner
    uploadOwnAvatar = 858 # Spending VC
    chooseDashboardBackground = 859 #Choose a background for the student dashboard
    getSurpriseAward = 860 #Get a small surprise award from the instructor
    chooseBackgroundForYourName = 861
    
    events = {
              startChallenge: {
                        'index': startChallenge,
                        'name':'startChallenge',
                        'displayName':'Start of Challenge',
                        'description':'Time when a student has started to attempt a particular challenge'
                        },
              endChallenge: {
                        'index': endChallenge,
                        'name':'endChallenge',
                        'displayName':'End of Challenge',
                        'description':'Time when a student has finished to attempt and has submitted a particular challenge'},
              completeQuestion: {
                        'index': completeQuestion,
                        'name':'completeQuestion',
                        'displayName':'Question Completed',
                        'description':'A student completes answering a particular question in a particular challenge'
                        },
              participationNoted: {
                        'index': participationNoted,
                        'name':'participationNoted',
                        'displayName':'Instructor Notes Participation',
                        'description':'An instructor acknowledges participation for a particular student for a particular activity'
                        },
              instructorAction: {
                        'index': instructorAction,
                        'name':'instructorAction',
                        'displayName':'Instructor Action',
                        'description':'An instructor awards points for a particular activity'
                        },
              timePassed: {
                        'index': timePassed,
                        'name':'timePassed',
                        'displayName':'Time Passed',
                        'description':'The duration/time limit of a challenge has been reached'
                        },
              valueChanged: {
                        'index': valueChanged,
                        'name':'valueChanged',
                        'displayName':'Variable Changes Value',
                        'description':'The value of a particular variable in a particular challenge is changed'
                        },
              startQuestion: {
                        'index': startQuestion,
                        'name':'startQuestion',
                        'displayName':'Start of Question',
                        'description':'Time when a student has started to attempt a particular question'
                        },
              endQuestion: {
                        'index': endQuestion,
                        'name':'endQuestion',
                        'displayName':'End of Question',
                        'description':'Time when a student has finished to attempt and has submitted a particular question'
                        },
              studentUpload: {
                        'index': studentUpload,
                        'name':'studentUpload',
                        'displayName':'Student Uploads Assignment',
                        'description':'A student uploads an assignment'
                        },
              leaderboardUpdate: {
                        'index': leaderboardUpdate,
                        'name':'leaderboardUpdate',
                        'displayName':'The Leaderboard is Updated',
                        'description':'The leaderboard is updated'
                        },

              userLogin: {
                        'index': userLogin,
                        'name':'userLogin',
                        'displayName':'User Login',
                        'description':'A student logs in with their credentials'
                          },
              challengeExpiration: {
                        'index': challengeExpiration,
                        'name':'challengeExpiration',
                        'displayName':'Challenge Expiration',
                        'description':'The time allowed for students to take a challenge expires.'
                          },
              buyHint: {
                        'index': buyHint,
                        'name':'buyHint',
                        'displayName':'Buy Hint',
                        'description':'Buy one hint for an assignment'
                        },
              buyAttempt: {
                        'index': buyAttempt,
                        'name':'buyAttempt',
                        'displayName':'Buy Attempt',
                        'description':'Buy a permission for one re-submission of an assignment'
                        },
              extendDeadline: {
                        'index': extendDeadline,
                        'name':'extendDeadline',
                        'displayName':'Extend Deadline',
                        'description':'Extend the due date for an assignment with 12 hours'
                        },              
              dropLowestAssignGrade: {
                        'index': dropLowestAssignGrade,
                        'name':'dropLowestAssignGrade',
                        'displayName':'Drop Lowest Assignment Grade',
                        'description':'Drop the lowest of your assignment grades'
                        },              
              getDifferentProblem: {
                        'index': getDifferentProblem,
                        'name':'getDifferentProblem',
                        'displayName':'Get Different Problem',
                        'description':'Get a different dynamic problem on a test'
                        },              
              seeClassAverage: {
                        'index': seeClassAverage,
                        'name':'seeClassAverage',
                        'displayName':'See Class Average',
                        'description':'See aggregated class information'
                        },  
              chooseLabPartner: {
                        'index': chooseLabPartner,
                        'name':'chooseLabPartner',
                        'displayName':'Choose Lab Partner',
                        'description':'Choose a lab partner'
                        },                            
              chooseProjectPartner: {
                        'index': chooseProjectPartner,
                        'name':'chooseProjectPartner',
                        'displayName':'Choose Project Partner',
                        'description':'Choose a project partner'
                        },                            
              uploadOwnAvatar: {
                        'index': uploadOwnAvatar,
                        'name':'uploadOwnAvatar',
                        'displayName':'Upload Own Avatar',
                        'description':'Upload your own avatar.'
                        },
              chooseDashboardBackground: {
                        'index': chooseDashboardBackground,
                        'name':'chooseDashboardBackground',
                        'displayName':'Choose Dashboard Background',
                        'description':'Choose a background for the your dashboard'
                        },
              chooseBackgroundForYourName: {
                        'index': chooseBackgroundForYourName,
                        'name':'chooseBackgroundForYourName',
                        'displayName':'Choose Background for Your Name',
                        'description':'Choose background or border for your name'
                        },              
              getSurpriseAward: {
                        'index': getSurpriseAward,
                        'name':'getSurpriseAward',
                        'displayName':'Get Surprise Award',
                        'description':'Get a small surprise award from the instructor'
                        }
                            
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
    objectTypes = {
        challenge:"challenge",
        activity:"activity",
        question:"question",
        form:"form",
        none:"global", # We would actually have called this "global" to begin with, but it's a reserved word.
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
    operandTypes={
        immediateInteger:'immediateInteger',
        condition:'condition',
        floatConstant:'floatConstant',
        stringConstant:'stringConstant',
        systemVariable:'systemVariable',
        challengeSet:'challengeSet',
        activitySet:'activitySet',
        conditionSet:'conditionSet',
        boolean:'boolean',
    }
    
class QuestionTypes():
    multipleChoice=1
    multipleAnswers=2
    matching=3
    trueFalse=4
    essay=5
    dynamic=6
    templatedynamic=7
    questionTypes={
        multipleChoice:{
           'index': multipleChoice,
           'name':'multipleChoice',
           'displayName':'Multiple Choice Questions',             
        },
        multipleAnswers:{
           'index': multipleAnswers,
           'name':'multipleAnswers',
           'displayName':'Multiple Answer Questions',             
        },            
        matching:{
           'index': matching,
           'name':'matching',
           'displayName':'Matching Questions',             
        },
        trueFalse:{
           'index': trueFalse,
           'name':'trueFalse',
           'displayName':'True/False Questions',             
        },
        essay:{
           'index': essay,
           'name':'essay',
           'displayName':'Essay Questions',             
        },
        dynamic:{
           'index': dynamic,
           'name':'dynamic',
           'displayName':'Dynamic Questions (Raw Lua)',                         
        },
        templatedynamic:{
           'index': templatedynamic,
           'name':'templatedynamic',
           'displayName':'Dynamic Questions (Template)',
        },  
    }   
    
