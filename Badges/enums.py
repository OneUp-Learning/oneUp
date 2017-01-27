
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
                'descrption': 'Give a student a notification'
                },
           lock:{
                'index':lock,
                'name': 'lock',
                'displayName': 'Lock?',
                'descrption': 'When a student completes answering a particular question in a particular challenge'
                },   
           unlock:{
                'index':unlock,
                'name': 'unlock',
                'displayName': 'Unlock?',
                'descrption': 'When an instructor enters some information for a particular activity'
                },
           setValue:{
                'index':setValue,
                'name': 'setValue',
                'displayName': 'Set Value',
                'descrption': 'Change the value of a variable'
                },
           addSkillPoints:{
                'index':addSkillPoints,
                'name': 'addSkillPoints',
                'displayName': 'Add Skill Points',
                'descrption': 'Add skill points'
                }
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
    
    events = {
              startChallenge: {
                          'index': startChallenge,
                          'name':'startChallenge',
                          'displayName':'Start of Challenge',
                          'description':'When a student has started to attempt a particular challenge'
                          },
              endChallenge: {
                        'index': endChallenge,
                        'name':'endChallenge',
                        'displayName':'End of Challenge',
                        'description':'When a student has finished to attempt and has submitted a particular challenge'},
              completeQuestion: {
                                 'index': completeQuestion,
                                 'name':'completeQuestion',
                                 'displayName':'Question Completed',
                                 'description':' When a student completes answering a particular question in a particular challenge'
                                 },
              participationNoted: {
                                   'index': participationNoted,
                                   'name':'participationNoted',
                                   'displayName':'Instructor Notes Participation',
                                   'description':'When an instructor acknowledges participation for a particular student for a particular activity'
                                   },
              timePassed: {
                           'index': timePassed,
                           'name':'timePassed',
                           'displayName':'Time Passed',
                           'description':'when the duration/time limit of a challenge has been reached'
                           },
              valueChanged: {
                            'index': valueChanged,
                            'name':'valueChanged',
                            'displayName':'Variable Changes Value',
                            'description':'When the value of a particular variable in a particular challenge is changed'
                            },
              startQuestion: {
                          'index': startQuestion,
                          'name':'startQuestion',
                          'displayName':'Start of Question',
                          'description':'When a student has started to attempt a particular question'
                          },
              endQuestion: {
                        'index': endQuestion,
                        'name':'endQuestion',
                        'displayName':'End of Question',
                        'description':'When a student has finished to attempt and has submitted a particular question'
                        },
              userLogin: {
                        'index': userLogin,
                        'name':'userLogin',
                        'displayName':'User Login',
                        'description':'When a student logs in with their credentials'
                          },
              challengeExpiration: {
                        'index': challengeExpiration,
                        'name':'challengeExpiration',
                        'displayName':'Challenge Expiration',
                        'description':'When the time allowed for students to take a challenge expires.'
                          }
              }
    

class SystemVariable():
    numAttempts = 901 # The total number of attempts that a student has given to a challenge
    testScore = 902 # The score for the challenge
    percentageCorrect = 903 # The percentage of correct answers that a student has answered in an(single) attempt for a particular challenge
    maxTestScore = 904 # The maximum of the test scores of all the student's attempts for a particular challenge
    minTestScore = 905 # The minimum of the test scores of all the student's attempts for a particular challenge
    dateOfFirstAttempt = 906 # The date on which the student has attempted a particular challenge for the first time.
    timeSpentOnChallenges = 907 # Time spent on a particular challenge.
    timeSpentOnQuestions = 908 # Time spent on a particular question. 
    consecutiveDaysLoggedIn = 909 # The number of consecutive days a student logs in to the One Up website
    activitiesCompleted = 910 # The number of activities a student has completed for a particular course
    challengeId = 911 # The challenge ID if a badge is to be awarded for a specific challenge - CHECK the notes fop this!
    systemVariables = {
                       numAttempts:{
                                    'index': numAttempts,
                                    'name':'numAttempts',
                                    'displayName':'Number of Attempts',
                                    'description':'The total number of attempts that a student has given to a challenge'
                                    },
                       testScore:{
                                  'index': testScore,
                                  'name':'testScore',
                                  'displayName':'Challenge Score',
                                  'description':'The score for the challenge'
                                  },
                       percentageCorrect:{
                                          'index': percentageCorrect,
                                          'name':'percentageCorrect',
                                          'displayName':'Percentage Correct',
                                          'description':'The percentage of correct answers that a student has answered in an(single) attempt for a particular challenge'
                                          },
                       maxTestScore:{
                                     'index': maxTestScore,
                                     'name':'maxTestScore',
                                     'displayName':'Maximum Challenge Score',
                                     'description':"The maximum of the test scores of all the student's attempts for a particular challenge"
                                     },
                       minTestScore:{
                                     'index': minTestScore,
                                     'name':'minTestScore',
                                     'displayName':'Minimum Challenge Score',
                                     'description':"The minimum of the test scores of all the student's attempts for a particular challenge"
                                     },
                       dateOfFirstAttempt:{
                                           'index': dateOfFirstAttempt,
                                           'name':'dateOfFirstAttempt',
                                           'displayName':'Date of First Attempt',
                                           'description':'The date on which the student has attempted a particular challenge for the first time.'
                                           },
                       timeSpentOnChallenges:{
                                       'index': timeSpentOnChallenges,
                                       'name':'timeSpentOnChallenges',
                                       'displayName':'Time Spent On Challenges',
                                       'description':'Total time spent in the Challenges section for a particular course.'
                                       },
                       timeSpentOnQuestions:{
                                       'index': timeSpentOnQuestions,
                                       'name':'timeSpentOnQuestions',
                                       'displayName':'Time Spent On Questions',
                                       'description':'Total time spent in the Questions section for a particular course.'
                                       },
                       consecutiveDaysLoggedIn:{
                                        'index':consecutiveDaysLoggedIn,
                                        'name':'consecutiveDaysLoggedIn',
                                        'displayName':'Consecutive Days Logged In',
                                        'description':'The number of consecutive days a student logs in to the One Up website.'        
                                        },
                       activitiesCompleted:{
                                        'index':activitiesCompleted,
                                        'name':'activitiesCompleted',
                                        'displayName':'Activities Completed',
                                        'description':'The number of activities a student has completed for a particular course.'  
                                        },
                       challengeId:{
                                    'index': challengeId,
                                    'name':'challengeId',
                                    'displayName':'Challenge ID',
                                    'description':'The challenge ID if a badge is to be awarded for a specific challenge'
                                    }
                       }

class OperandTypes():
    immediateInteger=1001
    condition=1002
    floatConstant=1003
    stringConstant=1004
    systemVariable=1005
    operandTypes={
        immediateInteger:'immediateInteger',
        condition:'condition',
        floatConstant:'floatConstant',
        stringConstant:'stringConstant',
        systemVariable:'systemVariable'
    }

class ObjectTypes():
    challenge=1301
    activity=1302
    question=1303
    form=1304 # Used in the case of handling general form submits (user login, etc.)
    
class QuestionTypes():
    multipleChoice=1
    multipleAnswers=2
    matching=3
    trueFalse=4
    essay=5
    dynamic=6
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
           'displayName':'Dynamic Questions',                         
        }                   
    }   
    
