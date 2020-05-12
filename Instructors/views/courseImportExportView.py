''' Created by Austin Hodge 5-18-19 '''

import json
import os
import zipfile
from decimal import Decimal
from distutils.dir_util import copy_tree

from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import HttpResponse, redirect, render
from django.utils import timezone

from Badges.conditions_util import (chosenObjectSpecifierFields,
                                    databaseConditionToJSONString,
                                    get_events_for_condition,
                                    operand_types_to_char,
                                    stringAndPostDictToCondition)
from Badges.enums import (Action, AwardFrequency, Event, ObjectTypes,
                          OperandTypes)
from Badges.models import (ActionArguments, ActivityCategorySet, ActivitySet,
                           AttendanceStreakConfiguration, Badges, BadgesInfo,
                           ChallengeSet, Conditions, ConditionSet,
                           CourseConfigParams, Dates, FloatConstants,
                           LeaderboardsConfig, PeriodicBadges,
                           ProgressiveUnlocking, RuleEvents, Rules,
                           StringConstants, TopicSet,
                           VirtualCurrencyCustomRuleInfo,
                           VirtualCurrencyPeriodicRule,
                           VirtualCurrencyRuleInfo)
from Badges.periodicVariables import (setup_periodic_badge,
                                      setup_periodic_leaderboard,
                                      setup_periodic_vc)
from Instructors.constants import (unassigned_problems_challenge_name,
                                   uncategorized_activity,
                                   unspecified_topic_name,
                                   unspecified_vc_manual_rule_name)
from Instructors.models import (Activities, ActivitiesCategory, Answers,
                                Challenges, ChallengesQuestions,
                                ChallengesTopics, ChallengeTags,
                                CorrectAnswers, Courses, CoursesSkills,
                                CoursesTopics, DynamicQuestions, LuaLibrary,
                                MatchingAnswers, QuestionLibrary,
                                QuestionProgrammingFiles, Questions,
                                QuestionsSkills, ResourceTags, Skills,
                                StaticQuestions, Tags,
                                TemplateDynamicQuestions, TemplateTextParts,
                                Topics, UploadedFiles)
from Instructors.questionTypes import QuestionTypes
from Instructors.views.utils import (current_localtime, date_to_selected,
                                     initialContextDict)
from oneUp.decorators import instructorsCheck
from Students.models import (StudentProgressiveUnlocking,
                             StudentRegisteredCourses)

# from io import BytesIO



#############################################################
# HELPER METHODS
#############################################################
# TODO: Timezone support. Be able to export datetimes which can be converted to another timezone
#       when importing.
LUA_PROBLEMS_ROOT = os.path.join(settings.BASE_DIR, 'lua/problems/')
VERSION = "1.0"

# Import: Fields that needs to be set when creating the model
# Export: Fields that needed to be exported to the json
# NOTE: If a model is a subclass you will need to also use the parent fields
model_lookup_table = {
    Topics: {
        'Import': {
            'topicName': None,
        },
        'Export': {
            'topicID': None,
            'topicName': None,
        }
    },
    CoursesTopics: {
        'Import': {
            'topicID': None,
            'courseID': None,
        },
        'Export': {
            'topicID': None,
            'topicName': None,
        }
    },
    Tags: {
        'Import': {}, # For now the tags are globally so we don't need to create any
        'Export': {
            'tagID': None,
            'tagName': None,
        }
    },
    ResourceTags: {
        'Import': {
            'tagID': None,
            'questionID': None,
        },
        'Export': {}
    },
    ChallengeTags: {
        'Import': {
            'tagID': None,
            'challengeID': None,
        },
        'Export': {}
    },
    ActivitiesCategory: {
        'Import': {
            'name': None,
            'courseID': None,
        },
        'Export': {
            'name': None,
            'categoryID': None,
        }
    },
    Skills: {
        'Import': {
            'skillName': None,
        },
        'Export': {
            'skillID': None,
            'skillName': None,
        }
    },
    CoursesSkills: {
        'Import': {
            'skillID': None,
            'courseID': None,
        },
        'Export': {}
    },
    Activities: {
        'Import': {
            'activityName': None,
            'isGraded': None,
            'description': None,
            'points': Decimal,
            'isFileAllowed': None,
            'uploadAttempts': None,
            'instructorNotes': None,
            'author': None,
            'hasStartTimestamp': None,
            'hasEndTimestamp': None,
            'hasDeadline': None,
            'courseID': None,
        },
        'Export': {
            'activityID': None,
            'activityName': None,
            'isGraded': None,
            'description': None,
            'points': str,
            'isFileAllowed': None,
            'uploadAttempts': None,
            'instructorNotes': None,
            'author': None,
        }
    },
    Challenges: {
        'Import': {
            'challengeName': None,
            'isGraded': None,
            'isRandomized': None,
            'numberAttempts': None,
            'timeLimit': None,
            'displayCorrectAnswer': None,
            'displayCorrectAnswerFeedback': None,
            'displayIncorrectAnswerFeedback': None,
            'challengeAuthor': None,
            'challengeDifficulty': None,
            'challengePassword': None,
            'hasStartTimestamp': None,
            'hasEndTimestamp': None,
            'hasDueDate': None,
            'courseID': None,
        },
        'Export': {
            'challengeID': None,
            'challengeName': None,
            'isGraded': None,
            'isRandomized': None,
            'numberAttempts': None,
            'timeLimit': None,
            'displayCorrectAnswer': None,
            'displayCorrectAnswerFeedback': None,
            'displayIncorrectAnswerFeedback': None,
            'challengeAuthor': None,
            'challengeDifficulty': None,
            'challengePassword': None,
        }
    },
    ChallengesTopics: {
        'Import':{
            'topicID': None,
            'challengeID': None,
        },
        'Export': {
            'topicID': None,
            'topicName': None,
        }
    },
    ChallengesQuestions: {
        'Import': {
            'points': Decimal,
            'challengeID': None,
            'questionID': None,
        },
        'Export': {
            'points': str,
        }
    },
    Questions: {
        'Import': {},
        'Export': {
            'questionID': str,
            'preview': None,
            'instructorNotes': None,
            'type': None,
            'difficulty': None,
            'author': None,
        }
    },
    DynamicQuestions: {
        'Import': {
            'preview': None,
            'instructorNotes': None,
            'type': None,
            'difficulty': None,
            'author': None,
            
            'numParts': None,
            'code': None,
            'submissionsAllowed': None,
            'resubmissionPenalty': None,
        },
        'Export': {
            'numParts': None,
            'code': None,
            'submissionsAllowed': None,
            'resubmissionPenalty': None,
        }
    },
    TemplateDynamicQuestions: {
        'Import': {
            'preview': None,
            'instructorNotes': None,
            'type': None,
            'difficulty': None,
            'author': None,

            'numParts': None,
            'code': None,
            'submissionsAllowed': None,
            'resubmissionPenalty': None,

            'templateText': None,
            'setupCode': None,
        },
        'Export': {
            'templateText': None,
            'setupCode': None,
        }
    },
    TemplateTextParts: {
        'Import': {
            'partNumber': None,
            'templateText': None,
            'dynamicQuestion': None,
            'pointsInPart': None,
        },
        'Export': {
            'partNumber': None,
            'templateText': None,
            'pointsInPart': None,
        }
    },
    QuestionProgrammingFiles: {
        'Import': {
            'questionID': None,
            'programmingFileName': None,
            'programmingFileFolderName': str,
            
        },
        'Export': {
            'programmingFileName': None,
            'programmingFileFolderName': None,
        }
    },
    QuestionLibrary: {
        'Import': {
            'question': None,
            'library': None,
        },
        'Export': {}
    },
    LuaLibrary: {
        'Import': {},
        'Export': {
            'libraryName': None,
        }
    },
    StaticQuestions: {
        'Import': {
            'preview': None,
            'instructorNotes': None,
            'type': None,
            'difficulty': None,
            'author': None,
            
            'questionText': None,
            'correctAnswerFeedback': None,
            'incorrectAnswerFeedback': None,
        },
        'Export': {
            'questionText': None,
            'correctAnswerFeedback': None,
            'incorrectAnswerFeedback': None,
        }
    },
    Answers: {
        'Import': {
            'answerText': None,
            'questionID': None,
        },
        'Export': {
            'answerText': None,
        }
    },
    CorrectAnswers: {
        'Import': {
            'answerID': None,
            'questionID': None,
        },
        'Export': {}
    },
    MatchingAnswers: {
        'Import': {
            'answerID': None,
            'questionID': None,
            'matchingAnswerText': None,
        },
        'Export': {
            'matchingAnswerText': None,
        }
    },
    QuestionsSkills: {
        'Import': {
            'skillID': None,
            'questionID': None,
            'questionSkillPoints': None,
            'courseID': None,
        },
        'Export': {
            'questionSkillPoints': None,
        }
    },
    Conditions: {
        'Import': {
            'courseID': None,
            'operation': None,
            'operand1Type': None,
            'operand1Value': int,
            'operand2Type': None,
            'operand2Value': int,
        },
        'Export': {
            # Done by databaseConditionToJSONString
        }
    },
    ConditionSet: {
        'Import': {
            'parentCondition': None,
            'conditionInSet': None,
        },
        'Export': {
            # Done by databaseConditionToJSONString
        }
    },
    ActivitySet: {
        'Import': {
            'activity_id': int,
            'condition': None,
        },
        'Export': {
            # Done by databaseConditionToJSONString
        }
    },
    ChallengeSet: {
        'Import': {
            'challenge_id': int,
            'condition': None,
        },
        'Export': {
            # Done by databaseConditionToJSONString
        }
    },
    TopicSet: {
        'Import': {
            'topic_id': int,
            'condition': None,
        },
        'Export': {
            # Done by databaseConditionToJSONString
        }
    },
    ActivityCategorySet: {
        'Import': {
            'category_id': int,
            'condition': None,
        },
        'Export': {
            # Done by databaseConditionToJSONString
        }
    },
    StringConstants: {
        'Import': {
            'stringValue': None,
        },
        'Export': {
            # Done by databaseConditionToJSONString
        }
    },
    Dates: {
        'Import': {
            'dateValue': None,
        },
        'Export': {
            # Done by databaseConditionToJSONString
        }
    },
    Rules: {
        'Import': {
            'courseID': None,
            'conditionID': None,
            'actionID': None,
            'objectSpecifier': None,
            'awardFrequency': None,
        },
        'Export': {
            'actionID': None,
            'awardFrequency': None,
        }
    },
    RuleEvents: {
        'Import': {
            'rule': None,
            'event': None,
            'inGlobalContext': None,
        },
        'Export': {}
    },
    Badges: {
        'Import': {
            'badgeName': None,
            'badgeDescription': None,
            'badgeImage': None,
            'manual': None,
            'isPeriodic': None,
            'courseID': None,

            'ruleID': None,
        },
        'Export': {
            'badgeName': None,
            'badgeDescription': None,
            'badgeImage': None,
            'manual': None,
            'isPeriodic': None,

            'actionID': None,
            'awardFrequency': None,
        }
    },
    PeriodicBadges: {
        'Import': {
            'badgeName': None,
            'badgeDescription': None,
            'badgeImage': None,
            'manual': None,
            'isPeriodic': None,
            'courseID': None,

            'periodicVariableID': None,
            'timePeriodID': None,
            'periodicType': None,
            'numberOfAwards': None,
            'threshold': None,
            'operatorType': None,
            'isRandom': None,
            'resetStreak': None,
            'lastModified': None,

            'periodicTask': None,
        },
        'Export': {
            'badgeName': None,
            'badgeDescription': None,
            'badgeImage': None,
            'manual': None,
            'isPeriodic': None,

            'periodicVariableID': None,
            'timePeriodID': None,
            'periodicType': None,
            'numberOfAwards': None,
            'threshold': None,
            'operatorType': None,
            'isRandom': None,
            'resetStreak': None,
        }
    },
    BadgesInfo: {
        'Import': {
            'badgeName': None,
            'badgeDescription': None,
            'badgeImage': None,
            'manual': None,
            'isPeriodic': None,
            'courseID': None,
        },
        'Export': {
            'badgeName': None,
            'badgeDescription': None,
            'badgeImage': None,
            'manual': None,
            'isPeriodic': None,
        }
    },
    ActionArguments: {
        'Import': {
            'ruleID': None,
            'sequenceNumber': None,
            'argumentValue': str,
        },
        'Export': {
            
        }
    },
    VirtualCurrencyRuleInfo: {
        'Import': {
            'vcRuleName': None,
            'vcRuleDescription': None,
            'vcRuleType': None,
            'vcRuleAmount': None,
            'vcAmountVaries': None,
            'vcRuleLimit': None,
            'isPeriodic': None,
            'courseID': None,

            'ruleID': None,
        },
        'Export': {
            'vcRuleName': None,
            'vcRuleDescription': None,
            'vcRuleType': None,
            'vcRuleAmount': None,
            'vcAmountVaries': None,
            'vcRuleLimit': None,
            'isPeriodic': None,

            'actionID': None,
            'awardFrequency': None,
        }
    },
    VirtualCurrencyPeriodicRule: {
        'Import': {
            'vcRuleName': None,
            'vcRuleDescription': None,
            'vcRuleType': None,
            'vcRuleAmount': None,
            'vcAmountVaries': None,
            'vcRuleLimit': None,
            'isPeriodic': None,
            'courseID': None,

            'periodicVariableID': None,
            'timePeriodID': None,
            'periodicType': None,
            'numberOfAwards': None,
            'threshold': None,
            'operatorType': None,
            'isRandom': None,
            'resetStreak': None,
            'lastModified': None,

            'periodicTask': None,
        },
        'Export': {
            'vcRuleName': None,
            'vcRuleDescription': None,
            'vcRuleType': None,
            'vcRuleAmount': None,
            'vcAmountVaries': None,
            'vcRuleLimit': None,
            'isPeriodic': None,

            'periodicVariableID': None,
            'timePeriodID': None,
            'periodicType': None,
            'numberOfAwards': None,
            'threshold': None,
            'operatorType': None,
            'isRandom': None,
            'resetStreak': None,
        }
    },
    VirtualCurrencyCustomRuleInfo: {
        'Import': {
            'vcRuleName': None,
            'vcRuleDescription': None,
            'vcRuleType': None,
            'vcRuleAmount': None,
            'vcAmountVaries': None,
            'vcRuleLimit': None,
            'isPeriodic': None,
            'courseID': None,
        },
        'Export': {
            'vcRuleName': None,
            'vcRuleDescription': None,
            'vcRuleType': None,
            'vcRuleAmount': None,
            'vcAmountVaries': None,
            'vcRuleLimit': None,
            'isPeriodic': None,
        }
    },
    LeaderboardsConfig: {
        'Import': {
            'leaderboardName': None, 
            'leaderboardDescription': None,
            'isContinous': None,
            'isXpLeaderboard': None, 
            'numStudentsDisplayed': None,
            'periodicVariable': None, 
            'timePeriodUpdateInterval': None, 
            'displayOnCourseHomePage': None, 
            'howFarBack': None,
            'lastModified': None,
            'courseID': None,

            'periodicTask': None,
        },
        'Export': {
            'leaderboardName': None, 
            'leaderboardDescription': None,
            'isContinous': None,
            'isXpLeaderboard': None, 
            'numStudentsDisplayed': None,
            'periodicVariable': None, 
            'timePeriodUpdateInterval': None, 
            'displayOnCourseHomePage': None, 
            'howFarBack': None,
        }
    },
    ProgressiveUnlocking: {
        'Import': {
            'name': None,
            'description': None,
            'objectID': None,
            'objectType': None,
            'courseID': None,

            'ruleID': None,
        },
        'Export': {
            'name': None,
            'description': None,
            'objectID': None,
            'objectType': None,
        }
    },
    StudentProgressiveUnlocking: {
        'Import': {
            'studentID': None,
            'pUnlockingRuleID': None,
            'courseID': None,
            'objectID': None,
            'objectType': None,
        },
        'Export': {}
    },
    AttendanceStreakConfiguration: {
        'Import': {
            'daysofClass': None,
            'daysDeselected': None,
            'courseID': None,
        },
        'Export': {
            'daysofClass': None,
            'daysDeselected': None,
        }
    }

}

def ensure_directory(directory):
    ''' Make sure the directory exists on the server (or locally) '''

    if not os.path.exists(directory):
        os.makedirs(directory)

def zip_directory(path, zip_handler, relative_path="lua/problems"):
    ''' Places a directory with all its contents into a zip file.
        
        path: absolute path to a directory
        relative_path: the directory to make inside the zip file 
    '''

    relative_path = os.path.join(relative_path, os.path.basename(path))
    folder_name = os.path.basename(path)

    for root, dirs, files in os.walk(path):
        arc_path = os.path.join(relative_path, os.path.basename(root))
        if os.path.basename(root) == folder_name:
            arc_path = relative_path

        for f in files:
            zip_handler.write(os.path.join(root, f), arcname=os.path.join(arc_path, f))

def create_item_node(query_object, fields_to_save):
    ''' Creates the key value pairs for json based on query object and
        which fields to save.

        field_to_save is list of tuples with value and cast specifier:
        ex. [("a", None), ("2", int), (4, str)]
    '''
    node = {}
    for field in fields_to_save:
        # Add key-val if the query object has this attribute (field)
        if hasattr(query_object, field[0]):
            value = getattr(query_object, field[0])
            # Cast the value if the field requires some casting
            if field[1] is not None:
                value = field[1](value)
                
            node[field[0]] = value
    return node

def create_item_node(query_object):
    ''' Creates the key value pairs for json based on query object and
        the Export fields in the model lookup table
    '''
    if not query_object:
        return {}

    node = {}
    model_type = type(query_object)
    print(model_type)

    for field_name, cast_specifier in model_lookup_table[model_type]['Export'].items():
        # Add key-val if the query object has this attribute (field)
        if hasattr(query_object, field_name):
            value = getattr(query_object, field_name)
            # Cast the value if the field requires some casting
            if cast_specifier is not None:
                value = cast_specifier(value)
                
            node[field_name] = value

    return node

def create_model_instance(model, fields_to_save, modify=False):
    ''' Creates a new instance of a model or modifies one  
        with the fields set from the fields_to_save argument.

        field_to_save is list of tuples with field name, value, and cast specifier:
        ex. [("a", "hello", None), ("score", 4, int), ("date", dt, str)]
    '''
    if modify:
        model_instance = model
    else:
        model_instance = model()

    for field in fields_to_save:
        value = field[1]
        # Cast the value if the field requires some casting
        if field[2] is not None:
            value = field[2](value)
        
        # Set the model field value
        setattr(model_instance, field[0], value)

    return model_instance

def create_model_instance(model, fields_data, custom_fields_to_save=None, modify=False):
    ''' Creates a new instance of a model or modifies one  
        with the fields set from the fields_to_save argument.

        fields_data is a json. usually from the imported json. It should contain
        field name and field value as key-value pairs

        custom_field_to_save is json with field name and value as key-value pairs:
        ex. {"a": "hello", "score": 4, "date": dt}

        NOTE: use custom_field_to_save parameter if you need to modify/create the 
        model instance with a custom value that is not in the fields_data json.
        custom_field_to_save will override field_data for the same field name.

    '''
    if modify:
        model_instance = model
        model_type = type(model)
    else:
        model_instance = model()
        model_type = model

    for field_name, cast_specifier in model_lookup_table[model_type]['Import'].items():
        if fields_data is None and custom_fields_to_save is None:
            continue
            
        value = None
        if fields_data and field_name in fields_data:
            value = fields_data[field_name]

        if custom_fields_to_save and field_name in custom_fields_to_save.keys():
            value = custom_fields_to_save[field_name]

        if value is None:
            continue

        # Cast the value if the field requires some casting
        if cast_specifier is not None:
            value = cast_specifier(value)
        
        # Set the model field value
        setattr(model_instance, field_name, value)

    return model_instance


def find_value_in_json(key, value, search_in=None):
    ''' Find a value inside of a list of jsons (python dicts) 
        value is tuple with cast specifier
        ex. (2, str)
        Returns True if found
    '''
    if search_in is None:
        return False
    
    for item in search_in:
        v = value[0]

        # Cast the value if the field requires some casting
        if value[1] is not None:
            v = value[1](value[0])

        if item[key] == v:
            return True

    return False

def search_for_mapped_id(search_in, for_id, id_map=None):
    ''' Searches for new mapped id given id map '''

    if not id_map or search_in not in id_map:
        return None
    
    # The id (key) to look for is not in the section to search in
    if for_id not in id_map[search_in]:
        return None

    return id_map[search_in][for_id]


#############################################################
# EXPORTING
#############################################################

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')  
def exportCourse(request):   
    ''' This is the main view where the exported course json will be saved to disk after calling the
        validateCourseExport view
    '''

    context_dict, current_course = initialContextDict(request)

    context_dict['version'] = VERSION

    if request.method == 'GET':
        return render(request,'Instructors/CourseExport.html', context_dict)
    
    if request.method == 'POST':
        
        root_json = json.loads(request.POST.get('exported-json', ''))
        # Only export json if the json contains items other than the version number
        if 'version' in root_json and len(root_json) > 1:
            file_name = 'media/textfiles/course/json/course-{}-{}.zip'.format(current_course.courseName, VERSION)
            ensure_directory('media/textfiles/course/json/')
            try:
                os.remove(file_name)
            except:
                print("File doesn't exist ", file_name)
            with zipfile.ZipFile(file_name, 'a') as zip_file:
                # Add the json for course
                zip_file.writestr('course.json', json.dumps(root_json).encode('utf-8'))
                
                # Add the folders to the zip file
                if 'code-paths' in root_json:
                    for path in root_json['code-paths']:
                        zip_directory(os.path.join(LUA_PROBLEMS_ROOT, path), zip_file)

                # print(zip_file.printdir())

            response = HttpResponse(open(file_name, 'rb'), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename=course-{}-{}.zip'.format(current_course.courseName, VERSION)

            return response
        
        return render(request,'Instructors/CourseExport.html', context_dict)

def validateCourseExport(request):
    ''' This view will build the json and check for any errors/warnings.
        It will return JSON response of both to ajax function so the user
        can decide if to continue saving exported course or fixed errors/warnings.
    '''

    context_dict, current_course = initialContextDict(request)
    if request.method == 'POST':
        if 'export' in request.POST:
            response = {}

            root_json = {}
            # Holds the messages to display for the user in the frontend
            messages = []
            
            # Send message if activities-categories are not selected but activities are
            if 'activities' in request.POST and 'activities-categories' not in request.POST:
                messages.append({'type': 'warn', 'message': 'Categories assigned in activities will not be exported. Please select Activities Categories when exporting to change this'})
            
            if ('serious-challenges' in request.POST or 'warmup-challenges' in request.POST or \
                'unassigned-problems' in request.POST) and 'skills' not in request.POST:
                messages.append({'type': 'warn', 'message': 'Skills assigned in problems will not be exported. Please select Skills when exporting to change this'})
            
            if ('serious-challenges' in request.POST or 'warmup-challenges' in request.POST) and \
                'topics' not in request.POST:
                messages.append({'type': 'warn', 'message': 'Topics assigned to challenges will not be exported. Please select Topics when exporting to change this'})

            if 'activities' in request.POST:
                # Notify user about fields not being exported 
                messages.append({'type': 'info', 'message': 'Activities Display From, Display To, and Due Date will not be exported. These options should be set after importing'})

            if 'serious-challenges' in request.POST or 'warmup-challenges' in request.POST:
                # Notify user about field export decisions
                messages.append({'type': 'info', 'message': 'Challenges Display From, Display To, and Due Date will not be exported. These options should be set after importing'})

            post_request = dict(request.POST)
            # Versioning
            root_json['version'] = VERSION

            # Create the json based on which checkbox is selected
            if 'topics' in request.POST:
                topics = CoursesTopics.objects.filter(courseID=current_course)
                root_json['topics'] = topics_to_json(topics, current_course, messages=messages)

            if 'activities-categories' in request.POST:
                activities_categories = ActivitiesCategory.objects.filter(courseID=current_course)
                root_json['activities-categories'] = activities_categories_to_json(activities_categories, current_course, messages=messages)
            
            if 'skills' in request.POST:
                course_skills = CoursesSkills.objects.filter(courseID=current_course)
                root_json['skills'] = course_skills_to_json(course_skills, current_course, messages=messages)

            if 'activities' in request.POST:
                activities = Activities.objects.filter(courseID=current_course)
                root_json['activities'] = activities_to_json(activities, current_course, include_categories='activities-categories' in request.POST, messages=messages)

            if 'serious-challenges' in request.POST:
                # Exclude unassigned challenge since that is created by default for every course
                serious_challenges = Challenges.objects.filter(courseID=current_course, isGraded=True).exclude(challengeName=unassigned_problems_challenge_name)
                root_json['serious-challenges'] = challenges_to_json(serious_challenges, current_course, include_topics='topics' in request.POST, root_json=root_json, messages=messages)

            if 'warmup-challenges' in request.POST:
                # Exclude unassigned challenge since that is created by default for every course
                warmup_challenges = Challenges.objects.filter(courseID=current_course, isGraded=False).exclude(challengeName=unassigned_problems_challenge_name)
                root_json['warmup-challenges'] = challenges_to_json(warmup_challenges, current_course, include_topics='topics' in request.POST, root_json=root_json, messages=messages)

            if 'unassigned-problems' in request.POST:
                unassigned_challenge = Challenges.objects.get(courseID=current_course, challengeName=unassigned_problems_challenge_name)
                challenge_questions = ChallengesQuestions.objects.filter(challengeID=unassigned_challenge)
                # Get only the challenge questions as json
                root_json['unassigned-problems'] = challenge_questions_to_json(challenge_questions, current_course, root_json=root_json, messages=messages)
            
            if 'automatic-badges' in request.POST:
                automatic_badges = Badges.objects.filter(courseID=current_course, manual=False, isPeriodic=False)
                root_json['automatic-badges'] = badges_to_json(automatic_badges, "automatic", current_course, post_request=post_request, root_json=root_json, messages=messages)
            
            if 'manual-badges' in request.POST:
                manual_badges = BadgesInfo.objects.filter(courseID=current_course, manual=True, isPeriodic=False)
                root_json['manual-badges'] = badges_to_json(manual_badges, "manual", current_course, messages=messages)
            
            if 'periodic-badges' in request.POST:
                periodic_badges = PeriodicBadges.objects.filter(courseID=current_course, manual=False, isPeriodic=True)
                root_json['periodic-badges'] = badges_to_json(periodic_badges, "periodic", current_course, messages=messages)
            
            if 'automatic-vc-rules' in request.POST:
                automatic_vc_rules = VirtualCurrencyRuleInfo.objects.filter(courseID=current_course, vcRuleType=True, isPeriodic=False)
                root_json['automatic-vc-rules'] = vc_rules_to_json(automatic_vc_rules, "automatic", current_course, post_request=post_request, root_json=root_json, messages=messages)
            
            if 'manual-vc-rules' in request.POST:
                # Get only the manual earning rules
                manual_vc_rules = VirtualCurrencyCustomRuleInfo.objects.filter(courseID=current_course, vcRuleType=True, isPeriodic=False).exclude(vcRuleName=unspecified_vc_manual_rule_name)
                manual_only_rules = [r.pk for r in manual_vc_rules if not hasattr(r, 'virtualcurrencyruleinfo') and not hasattr(r, 'virtualcurrencyperiodicrule')]
                manual_vc_rules = VirtualCurrencyCustomRuleInfo.objects.filter(pk__in=manual_only_rules)
                root_json['manual-vc-rules'] = vc_rules_to_json(manual_vc_rules, "manual", current_course, messages=messages)
            
            if 'periodic-vc-rules' in request.POST:
                periodic_vc_rules = VirtualCurrencyPeriodicRule.objects.filter(courseID=current_course, isPeriodic=True)
                root_json['periodic-vc-rules'] = vc_rules_to_json(periodic_vc_rules, "periodic", current_course, messages=messages)
            
            if 'spending-vc-rules' in request.POST:
                spending_vc_rules = VirtualCurrencyRuleInfo.objects.filter(courseID=current_course, vcRuleType=False, isPeriodic=False)
                root_json['spending-vc-rules'] = vc_rules_to_json(spending_vc_rules, "spending", current_course, post_request=post_request, root_json=root_json, messages=messages)

            if 'leaderboards' in request.POST:
                # Exclude XP Leaderboard since it is created in prefrences (probably should be created when course is created instead)
                leaderboards = LeaderboardsConfig.objects.filter(courseID=current_course).exclude(isXpLeaderboard=True)
                root_json['leaderboards'] = leaderboards_to_json(leaderboards, current_course, messages=messages)

            if 'content-unlocking' in request.POST:
                unlocking_rules = ProgressiveUnlocking.objects.filter(courseID=current_course)
                root_json['content-unlocking'] = content_unlocking_rules_to_json(unlocking_rules, current_course, post_request=post_request, root_json=root_json, messages=messages)

            if 'streaks' in request.POST:
                streaks = AttendanceStreakConfiguration.objects.filter(courseID=current_course)
                root_json['streaks'] = streaks_to_json(streaks, current_course, messages=messages)

            # Get rid of duplicate messages by converting list of dicts 
            # to set of tuples then back to list of dicts
            messages = [dict(t) for t in {tuple(d.items()) for d in messages}]
            response['messages'] = messages
            
            response['exported-json'] = root_json
            # Debug messages
            # ensure_directory('media/textfiles/course/json/')
            # with open('media/textfiles/course/json/export-log.json', 'w') as export_stream:
            #     json.dump(messages, export_stream)

            return JsonResponse(response)
    
    return JsonResponse({'messages': [{'type': 'error', 'message': 'Error in validation export course request'}]})

#############################################################
# EXPORTING JSON VALIDATION
#############################################################

def validate_rule_json(rule_json, post_request, root_json=None, messages=[]):
    ''' Validates a rule condition and object specifier to check to see if 
        object ids referenced are in the root_json
    '''
    # Validate object specifier for this rule
    object_type = AwardFrequency.awardFrequency[rule_json['awardFrequency']]['objectType']
    validate_object_specifier_json(rule_json['objectSpecifier'], object_type, post_request, root_json=root_json, messages=messages)

    # Validate condition for this rule
    validate_condition_json(rule_json['condition'], post_request, root_json, messages=messages)       

def validate_content_unlocking_rule_json(content_unlocking_rule_json, post_request, root_json=None, messages=[]):
    ''' Validates a content unlocking rule to see if a 
        object id is in the root_json
    '''
    if not content_unlocking_rule_json:
        return
    
    if 'objectID' in content_unlocking_rule_json and 'objectType' in content_unlocking_rule_json:
        object_type = content_unlocking_rule_json['objectType']
        object_id = content_unlocking_rule_json['objectID']

        if object_type == ObjectTypes.none:
            pass
        elif object_type == ObjectTypes.challenge:
            if 'serious-challenges' not in post_request and 'warmup-challenges' not in post_request:
                # Send warning message
                messages.append({'type': 'warn', 'message': 'Unable to find challenge ids for content unlocking rule. Make sure serious challenge and/or warmup challenges are being exported'})
                return

            # Find the id in the root_json
            are_serious_challenges_being_exported = None
            are_warmup_challenges_being_exported = None

            if 'serious-challenges' in root_json:
                are_serious_challenges_being_exported = find_value_in_json('challengeID', (object_id, int), search_in=root_json['serious-challenges'])

            if 'warmup-challenges' in root_json:
                are_warmup_challenges_being_exported = find_value_in_json('challengeID', (object_id, int), search_in=root_json['warmup-challenges'])

            if are_serious_challenges_being_exported == None and are_warmup_challenges_being_exported == None:
                # Safety check just in case either serious-challenges or warmup challenges are not in the root_json
                messages.append({'type': 'error', 'message': 'ummmmm you shouldnt be reading this (challenge content unlocking)'})
                return
            
            if (are_serious_challenges_being_exported == False and are_warmup_challenges_being_exported == False) or \
                (are_warmup_challenges_being_exported == None and are_serious_challenges_being_exported == False) or \
                (are_warmup_challenges_being_exported == False and are_serious_challenges_being_exported == None):
                # Send error message
                messages.append({'type': 'error', 'message': 'Unable to find challenge id for content unlocking rule when exporting'})
                return

            
        elif object_type == ObjectTypes.activity:
           
            if 'activities' not in post_request:
                # Send warning message
                messages.append({'type': 'warn', 'message': 'Unable to find activity ids for content unlocking rule. Make sure activities are being exported'})
                return

            # Find the id in the root_json
            are_activities_being_exported = find_value_in_json('activityID', (object_id, int), search_in=root_json['activities'])

            if are_activities_being_exported == None:
                # Safety check just in case activities are not in the root_json
                messages.append({'type': 'error', 'message': 'ummmmm you shouldnt be reading this (activity content unlocking rule)'})
                return
            
            if are_activities_being_exported == False:
                # Send error message
                messages.append({'type': 'error', 'message': 'Unable to find activity id for content unlocking rule when exporting'})
                return

        elif object_type == ObjectTypes.topic:

            if 'topics' not in post_request:
                # Send warning message
                messages.append({'type': 'warn', 'message': 'Unable to find topic ids for content unlocking rule. Make sure topics are being exported'})
                return

            # Find the id in the root_json
            are_topics_being_exported = find_value_in_json('topicID', (object_id, int), search_in=root_json['topics'])

            if are_topics_being_exported == None:
                # Safety check just in case topics are not in the root_json
                messages.append({'type': 'error', 'message': 'ummmmm you shouldnt be reading this (topic content unlocking rule)'})
                return
            
            if are_topics_being_exported == False:
                # Send error message
                messages.append({'type': 'error', 'message': 'Unable to find topic id for content unlocking rule when exporting'})
                return

        elif object_type == ObjectTypes.activityCategory:
            
            if 'activities-categories' not in post_request:
                # Send warning message
                messages.append({'type': 'warn', 'message': 'Unable to find activity category ids for content unlocking rule. Make sure activities categories are being exported'})
                return

            are_activities_categories_being_exported = find_value_in_json('categoryID', (object_id, int), search_in=root_json['activities-categories'])

            if are_activities_categories_being_exported == None:
                # Safety check just in case activities-categories are not in the root_json
                messages.append({'type': 'error', 'message': 'ummmmm you shouldnt be reading this (activity category content unlocking rule)'})
                return
            
            if are_activities_categories_being_exported == False:
                # Send error message
                messages.append({'type': 'error', 'message': 'Unable to find activity category id for content unlocking rule when exporting'})
                return

def validate_object_specifier_json(object_specifier_json, object_type, post_request, root_json=None, messages=[]):
    ''' Make sure the object ids (challenges, activities, topics, activitycategory) in the 
        object specifier is being exported as well in the json
    '''

    if not object_specifier_json:
        return

    if object_type == ObjectTypes.none:
        pass
    elif object_type == ObjectTypes.challenge:
        for specifier in object_specifier_json:
            if not specifier['value']:
                continue

            if specifier['specifier'] == 'id':
                if 'serious-challenges' not in post_request and 'warmup-challenges' not in post_request:
                    # Send warning message
                    messages.append({'type': 'warn', 'message': 'Unable to find challenge ids for object specifiers. Make sure serious challenge and/or warmup challenges are being exported'})
                    break

                for object_id in specifier['value']:
                    # Find the id in the root_json
                    are_serious_challenges_being_exported = None
                    are_warmup_challenges_being_exported = None
                    if 'serious-challenges' in root_json:
                        are_serious_challenges_being_exported = find_value_in_json('challengeID', (object_id, int), search_in=root_json['serious-challenges'])

                    if 'warmup-challenges' in root_json:
                        are_warmup_challenges_being_exported = find_value_in_json('challengeID', (object_id, int), search_in=root_json['warmup-challenges'])

                    if are_serious_challenges_being_exported == None and are_warmup_challenges_being_exported == None:
                        # Safety check just in case either serious-challenges or warmup challenges are not in the root_json
                        messages.append({'type': 'error', 'message': 'ummmmm you shouldnt be reading this (challenge specifier)'})
                        break
                    
                    if (are_serious_challenges_being_exported == False and are_warmup_challenges_being_exported == False) or \
                        (are_warmup_challenges_being_exported == None and are_serious_challenges_being_exported == False) or \
                        (are_warmup_challenges_being_exported == False and are_serious_challenges_being_exported == None):
                        # Send error message
                        messages.append({'type': 'error', 'message': 'Unable to find challenge id for object specifier when exporting'})
                        break

            elif specifier['specifier'] == 'type':
                if 'serious-challenges' not in post_request and 'warmup-challenges' not in post_request:
                    # Send warning message
                    messages.append({'type': 'warn', 'message': 'Unable to find challenge ids for object specifiers. Make sure serious challenge and/or warmup challenges are being exported'})
                    break

            elif specifier['specifier'] == 'topic':
                if 'topics' not in post_request:
                    # Send warning message
                    messages.append({'type': 'warn', 'message': 'Unable to find topic ids for object specifiers. Make sure topics are being exported'})
                    break
                
                for object_id in specifier['value']:
                    are_topics_being_exported = find_value_in_json('topicID', (object_id, int), search_in=root_json['topics'])

                    if are_topics_being_exported == None:
                        # Safety check just in case topics are not in the root_json
                        messages.append({'type': 'error', 'message': 'ummmmm you shouldnt be reading this (topic specifier)'})
                        break
                    
                    if are_topics_being_exported == False:
                        # Send error message
                        messages.append({'type': 'error', 'message': 'Unable to find topic id for object specifier when exporting'})
                        break
        
    elif object_type == ObjectTypes.activity:
        for specifier in object_specifier_json:
            if not specifier['value']:
                continue

            if specifier['specifier'] == 'id':
                if 'activities' not in post_request:
                    # Send warning message
                    messages.append({'type': 'warn', 'message': 'Unable to find activity ids for object specifiers. Make sure activities are being exported'})
                    break

                for object_id in specifier['value']:
                    # Find the id in the root_json
                    are_activities_being_exported = find_value_in_json('activityID', (object_id, int), search_in=root_json['activities'])

                    if are_activities_being_exported == None:
                        # Safety check just in case activities are not in the root_json
                        messages.append({'type': 'error', 'message': 'ummmmm you shouldnt be reading this (activity specifier)'})
                        break
                    
                    if are_activities_being_exported == False:
                        # Send error message
                        messages.append({'type': 'error', 'message': 'Unable to find activity id for object specifier when exporting'})
                        break

            elif specifier['specifier'] == 'category':
                if 'activities-categories' not in post_request:
                    # Send warning message
                    messages.append({'type': 'warn', 'message': 'Unable to find activity category ids for object specifiers. Make sure activities categories are being exported'})
                    break

                for object_id in specifier['value']:
                    are_activities_categories_being_exported = find_value_in_json('categoryID', (object_id, int), search_in=root_json['activities-categories'])

                    if are_activities_categories_being_exported == None:
                        # Safety check just in case activities categories are not in the root_json
                        messages.append({'type': 'error', 'message': 'ummmmm you shouldnt be reading this (activity-activity category specifier)'})
                        break
                    
                    if are_activities_categories_being_exported == False:
                        # Send error message
                        messages.append({'type': 'error', 'message': 'Unable to find activity category id for object specifier when exporting'})
                        break

    elif object_type == ObjectTypes.topic:
        for specifier in object_specifier_json:
            if not specifier['value']:
                continue

            if specifier['specifier'] == 'id':
                if 'topics' not in post_request:
                    # Send warning message
                    messages.append({'type': 'warn', 'message': 'Unable to find topic ids for object specifiers. Make sure topics are being exported'})
                    break

                for object_id in specifier['value']:
                    # Find the id in the root_json
                    are_topics_being_exported = find_value_in_json('topicID', (object_id, int), search_in=root_json['topics'])

                    if are_topics_being_exported == None:
                        # Safety check just in case topics are not in the root_json
                        messages.append({'type': 'error', 'message': 'ummmmm you shouldnt be reading this (topic specifier)'})
                        break
                    
                    if are_topics_being_exported == False:
                        # Send error message
                        messages.append({'type': 'error', 'message': 'Unable to find topic id for object specifier when exporting'})
                        break

    elif object_type == ObjectTypes.activityCategory:
        for specifier in object_specifier_json:
            if not specifier['value']:
                continue

            if specifier['specifier'] == 'id':
                if 'activities-categories' not in post_request:
                    # Send warning message
                    messages.append({'type': 'warn', 'message': 'Unable to find activity category ids for object specifiers. Make sure activities categories are being exported'})
                    break

                for object_id in specifier['value']:
                    are_activities_categories_being_exported = find_value_in_json('categoryID', (object_id, int), search_in=root_json['activities-categories'])

                    if are_activities_categories_being_exported == None:
                        # Safety check just in case activities-categories are not in the root_json
                        messages.append({'type': 'error', 'message': 'ummmmm you shouldnt be reading this (activity category specifier)'})
                        break
                    
                    if are_activities_categories_being_exported == False:
                        # Send error message
                        messages.append({'type': 'error', 'message': 'Unable to find activity category id for object specifier when exporting'})
                        break

def validate_condition_json(condition_json, post_request, root_json, messages=[]):
    ''' Make sure the object ids (challenges, activities, topics, activitycategory) in the 
        for all/any conditions are being exported as well in the json
    '''

    if not condition_json or root_json is None:
        return
    # ATOMs do not have object ids
    if condition_json['type'] == 'ATOM':
        return
    # ANDs and ORs contains list of ATOMs or FORs
    if condition_json['type'] == 'AND' or condition_json['type'] == 'OR':
        for condition in condition_json['subConds']:
            validate_condition_json(condition, post_request, root_json)
    
    # FORs contains objects ids
    if condition_json['type'] == 'FOR':
        # Don't continue if there are no object ids
        if not condition_json['objects']:
            return

        if condition_json['objectType'] == 'challenge':
            if 'serious-challenges' not in post_request and 'warmup-challenges' not in post_request:
                # Send warning message
                messages.append({'type': 'warn', 'message': 'Unable to find challenge ids for conditions. Make sure serious challenge and/or warmup challenges are being exported'})
                return

            for object_id in condition_json['objects']:
                # Find the id in the root_json
                are_serious_challenges_being_exported = None
                are_warmup_challenges_being_exported = None
                if 'serious-challenges' in root_json:
                    are_serious_challenges_being_exported = find_value_in_json('challengeID', (object_id, int), search_in=root_json['serious-challenges'])

                if 'warmup-challenges' in root_json:
                    are_warmup_challenges_being_exported = find_value_in_json('challengeID', (object_id, int), search_in=root_json['warmup-challenges'])

                if are_serious_challenges_being_exported == None and are_warmup_challenges_being_exported == None:
                    # Safety check just in case either serious-challenges or warmup challenges are not in the root_json
                    messages.append({'type': 'error', 'message': 'ummmmm you shouldnt be reading this (challenge)'})
                    return
                
                if (are_serious_challenges_being_exported == False and are_warmup_challenges_being_exported == False) or \
                    (are_warmup_challenges_being_exported == None and are_serious_challenges_being_exported == False) or \
                    (are_warmup_challenges_being_exported == False and are_serious_challenges_being_exported == None):
                    # Send error message
                    messages.append({'type': 'error', 'message': 'Unable to find challenge id for condition when exporting'})
                    return

        elif condition_json['objectType'] == 'activity':
            if 'activities' not in post_request:
                # Send warning message
                messages.append({'type': 'warn', 'message': 'Unable to find activity ids for conditions. Make sure activities are being exported'})
                return

            for object_id in condition_json['objects']:
                are_activities_being_exported = find_value_in_json('activityID', (object_id, int), search_in=root_json['activities'])

                if are_activities_being_exported == None:
                    # Safety check just in case activities are not in the root_json
                    messages.append({'type': 'error', 'message': 'ummmmm you shouldnt be reading this (activity)'})
                    return
                
                if are_activities_being_exported == False:
                    # Send error message
                    messages.append({'type': 'error', 'message': 'Unable to find activity id for condition when exporting'})
                    return

        elif condition_json['objectType'] == 'topic':
            if 'topics' not in post_request:
                # Send warning message
                messages.append({'type': 'warn', 'message': 'Unable to find topic ids for conditions. Make sure topics are being exported'})
                return

            for object_id in condition_json['objects']:
                are_topics_being_exported = find_value_in_json('topicID', (object_id, int), search_in=root_json['topics'])

                if are_topics_being_exported == None:
                    # Safety check just in case topics are not in the root_json
                    messages.append({'type': 'error', 'message': 'ummmmm you shouldnt be reading this (topic)'})
                    return
                
                if are_topics_being_exported == False:
                    # Send error message
                    messages.append({'type': 'error', 'message': 'Unable to find topic id for condition when exporting'})
                    return
                
        elif condition_json['objectType'] == 'category':
            if 'activities-categories' not in post_request:
                # Send warning message
                messages.append({'type': 'warn', 'message': 'Unable to find activity category ids for conditions. Make sure activities categories are being exported'})
                return

            for object_id in condition_json['objects']:
                are_activities_categories_being_exported = find_value_in_json('categoryID', (object_id, int), search_in=root_json['activities-categories'])

                if are_activities_categories_being_exported == None:
                    # Safety check just in case activities-categories are not in the root_json
                    messages.append({'type': 'error', 'message': 'ummmmm you shouldnt be reading this (activity category)'})
                    return
                
                if are_activities_categories_being_exported == False:
                    # Send error message
                    messages.append({'type': 'error', 'message': 'Unable to find activity category id for condition when exporting'})
                    return

#############################################################
# EXPORTING JSON METHODS
#############################################################

def challenges_to_json(challenges, current_course, include_topics=True, post_request=None, root_json=None, messages=[]):
    ''' Converts challenges queryset to json '''

    challenges_jsons = []

    if challenges.exists():

        for challenge in challenges:
            # Get the challenge information
            challenge_details = create_item_node(challenge)

            if include_topics:
                # Add topics for this challenge if any
                challenge_topics = ChallengesTopics.objects.filter(challengeID=challenge)
                if challenge_topics.exists(): 
                    # Add to challenge details
                    challenge_details['topics'] = topics_to_json(challenge_topics, current_course, messages=[])

            # Add any tags for this challenge
            challenge_tags = Tags.objects.filter(tagID__in=ChallengeTags.objects.filter(challengeID=challenge).values_list('tagID'))
            challenge_details['tags'] = tags_to_json(challenge_tags, messages=[])
            print(challenge_details['tags'])
            # Add questions for this challenges
            challenge_questions = ChallengesQuestions.objects.filter(challengeID=challenge)

            # Add the questions to the challenge object
            challenge_details['challenge-questions'] = challenge_questions_to_json(challenge_questions, current_course, root_json=root_json, post_request=post_request, messages=[])

            challenges_jsons.append(challenge_details)

    return challenges_jsons

def challenge_questions_to_json(challenge_questions, current_course, post_request=None, root_json=None, messages=[]):
    ''' Converts challenge questions queryset to json '''

    challenge_questions_jsons = []

    if challenge_questions.exists():

        for challenge_question in challenge_questions:
            # Add the challenge question model details
            challenge_question_details = create_item_node(challenge_question)
            
            # Add the question model details
            question = challenge_question.questionID
            question_details = create_item_node(question)

            # Add the question skills if any
            question_skills = QuestionsSkills.objects.filter(questionID=question, courseID = current_course)
            if question_skills.exists():
                question_skills_jsons = []

                for skill in question_skills: 
                    skill_details = create_item_node(skill)
                    # Add the skill id and name
                    skill_details.update(create_item_node(skill.skillID))

                    question_skills_jsons.append(skill_details)

                # Add questions skills to the question model details
                question_details['skills'] = question_skills_jsons

            # Add any tags for this question
            question_tags = Tags.objects.filter(tagID__in=ResourceTags.objects.filter(questionID=question).values_list('tagID'))
            question_details['tags'] = tags_to_json(question_tags, messages=[])

            # Add the Static Question if it is this type
            static_questions = StaticQuestions.objects.filter(questionID=int(question.questionID))
            if static_questions.exists():
                static_question = static_questions.first()
                static_question_details = create_item_node(static_question)

                # Add Answers for Static Questions
                static_question_answers = Answers.objects.filter(questionID=static_question)    
                
                static_question_answers_jsons = []
                for answer in static_question_answers:            
                    answer_details = create_item_node(answer)
                
                    # Check if it is a correct answer
                    correct_answers = CorrectAnswers.objects.filter(questionID=static_question, answerID = answer)
                    if correct_answers.exists():
                        answer_details['correctAnswer'] = True
                        
                    # Check if this answer has a matching answer
                    if challenge_question.questionID.type == QuestionTypes.matching:                                               
                        matching_answer = MatchingAnswers.objects.get(answerID=answer, questionID=static_question) 
                        if matching_answer:
                            answer_details.update(create_item_node(matching_answer))

                    # Add answer detail to static question json list
                    static_question_answers_jsons.append(answer_details)
                
                # Add the static questions answers to the static question overall detail information
                static_question_details['answers'] = static_question_answers_jsons

                # Add the static question to the question details
                question_details['static-question'] = static_question_details


            # Add the Dynamic Question if it is this type
            dynamic_questions = DynamicQuestions.objects.filter(questionID=int(question.questionID))
            if dynamic_questions.exists():
                dynamic_question = dynamic_questions.first()

                dynamic_question_details = create_item_node(dynamic_question)
        
                # Add the TemplateDynamicQuestions if any
                template_dynamic_questions = TemplateDynamicQuestions.objects.filter(questionID=int(question.questionID))
                if template_dynamic_questions.exists():
                    template_dynamic_question = template_dynamic_questions.first()

                    template_dynamic_question_details = create_item_node(template_dynamic_question)
    
                    # Add the TemplateTextParts
                    template_text_parts = TemplateTextParts.objects.filter(dynamicQuestion=question)
                    if template_text_parts.exists():  
                                              
                        template_text_parts_jsons = []
                        for part in template_text_parts:    
                            template_text_part_details = create_item_node(part)
                            template_text_parts_jsons.append(template_text_part_details)
                        # Add the template parts to the tempalte dyanmic question
                        template_dynamic_question_details['template-text-parts'] = template_text_parts_jsons

                    # Add template dynamic question to dynamic question
                    dynamic_question_details['template-dynamic-question'] = template_dynamic_question_details

                # Add QuestionProgrammingFiles if any. problems stored in lua/problems
                # Folder name is question id
                question_programming_files = QuestionProgrammingFiles.objects.filter(questionID=question)
                if question_programming_files.exists():
                    question_programming_files_jsons = []
                    for question_programming_file in question_programming_files:     
                        question_programming_file_details = create_item_node(question_programming_file) # LuaLibrary model
                        
                        # Store which folder this question belongs too so we can find it when importing
                        if not 'code-paths' in root_json:
                            root_json['code-paths'] = []

                        root_json['code-paths'].append(question_programming_file.programmingFileFolderName)
                        
                        question_programming_files_jsons.append(question_programming_file_details)

                    # Add question libraries to dynamic question details
                    dynamic_question_details['question-programming-files'] = question_programming_files_jsons

                # Add QuestionLibrary if any
                question_libraries = QuestionLibrary.objects.filter(question=question)
                if question_libraries.exists():
                    question_libraries_jsons = []
                    for question_library in question_libraries:     
                        question_library_details = create_item_node(question_library.library) # LuaLibrary model
                        question_libraries_jsons.append(question_library_details)

                    # Add question libraries to dynamic question details
                    dynamic_question_details['question-libraries'] = question_libraries_jsons

                # Add dynamic question to the question details
                question_details['dynamic-question'] = dynamic_question_details

            # Add the question detail into the challenge question detail that holds the points information
            challenge_question_details['question'] = question_details

            # Add the question into the list of challenge questions jsons
            challenge_questions_jsons.append(challenge_question_details)

    return challenge_questions_jsons

def activities_to_json(activities, current_course, include_categories=True, post_request=None, root_json=None, messages=[]):
    ''' Converts activities queryset to json '''

    activities_jsons = []

    if activities.exists():

        for activity in activities:
            # Get the activity information
            activity_details = create_item_node(activity)

            # NOTE: we are also including Uncategorized category just in case to map the id  
            # if it has been used in conditions rules
            if include_categories:
                # Save the activity category
                activity_details['category'] = create_item_node(activity.category)

            # Add the activity details to the activities json list
            activities_jsons.append(activity_details)

    return activities_jsons

def activities_categories_to_json(activities_categories, current_course, post_request=None, root_json=None, messages=[]):
    ''' Converts Activity Categories queryset to json '''

    activities_categories_jsons = []

    if activities_categories.exists(): 
        for category in activities_categories:
            # NOTE: we are also including Uncategorized category just in case to map the id  
            # if it has been used in conditions rules
            
            # Get category information
            activity_category_details = create_item_node(category)
            
            activities_categories_jsons.append(activity_category_details)

    return activities_categories_jsons

def badges_to_json(badges, badge_type, current_course, post_request=None, root_json=None, messages=[]):
    ''' Converts Badges queryset to json '''
    
    badges_jsons = []

    if badges.exists():

        for badge in badges:
            # Get basic badge information
            badge_details = create_item_node(badge)

            if badge_type == 'automatic':
                automatic_badge_rule = badge.ruleID

                # Get the badge rule details
                automatic_badge_rule_details = rule_model_to_json(automatic_badge_rule)

                # Check to see if the conditions & specifier object ids are being exported as well
                if post_request:
                    validate_rule_json(automatic_badge_rule_details, post_request, root_json=root_json, messages=messages)

                badge_details['rule'] = automatic_badge_rule_details

            elif badge_type == 'periodic':
                # Add periodic badge details to badge details
                perioidc_badge_details = create_item_node(badge)

                badge_details.update(perioidc_badge_details)
            

            badges_jsons.append(badge_details)

    return badges_jsons

def vc_rules_to_json(vc_rules, vc_rule_type, current_course, post_request=None, root_json=None, messages=[]):
    ''' Converts Virtual Currency Rules to json '''
    
    vc_rules_jsons = []

    if vc_rules.exists():
       
        for vc_rule in vc_rules:
            # Get basic badge information
            vc_rule_details = create_item_node(vc_rule)

            if vc_rule_type == 'automatic':
                automatic_vc_rule = vc_rule.ruleID

                # Get the vc rule details
                automatic_vc_rule_details = rule_model_to_json(automatic_vc_rule)
                automatic_vc_rule_details['vcRuleAmount'] = ActionArguments.objects.get(ruleID=automatic_vc_rule).argumentValue
                # Check to see if the conditions & specifier object ids are being exported as well
                if post_request:
                    validate_rule_json(automatic_vc_rule_details, post_request, root_json=root_json, messages=messages)

                vc_rule_details['rule'] = automatic_vc_rule_details
            
            elif vc_rule_type == 'periodic':
                # Add periodic vc rule details to vc rule details
                perioidc_vc_rule_details = create_item_node(vc_rule)

                vc_rule_details.update(perioidc_vc_rule_details)            

            vc_rules_jsons.append(vc_rule_details)

    return vc_rules_jsons

def rule_model_to_json(automatic_rule):
    ''' Converts a Rule to json for models:
        Badges, VirtualCurrencyRuleInfo
    '''

    if automatic_rule:
        # Get the rule information
        automatic_rule_details = create_item_node(automatic_rule)

        # Setup Object specifier
        automatic_rule_object_specifier = automatic_rule.objectSpecifier
        automatic_rule_details['objectSpecifier'] = json.loads(automatic_rule_object_specifier)
        # Get the rule condition string
        automatic_rule_condition = automatic_rule.conditionID
        automatic_rule_details['condition'] = json.loads(databaseConditionToJSONString(automatic_rule_condition))

        return automatic_rule_details

    return None

def topics_to_json(topics, current_course, post_request=None, root_json=None, messages=[]):
    ''' Converts topics (Course Topics or Challenge Topics) queryset to json '''

    topics_jsons = []

    if topics.exists():

        for course_topic in topics:
            # NOTE: we are also including Unspecified topic just in case to map the id 
            # if it has been used in conditions rules

            topic = course_topic.topicID
            # Get the topic information
            topic_details = create_item_node(topic)

            topics_jsons.append(topic_details)

    return topics_jsons

def course_skills_to_json(course_skills, current_course, post_request=None, root_json=None, messages=[]):
    ''' Converts skills (CoursesSkills) queryset to json '''

    course_skills_jsons = []

    if course_skills.exists():

        for course_skill in course_skills: 
            skill = course_skill.skillID
            # Get the skills details into json
            skill_details = create_item_node(skill)
            # Add to json list
            course_skills_jsons.append(skill_details)

    return course_skills_jsons

def tags_to_json(tags, post_request=None, root_json=None, messages=[]):
    tags_jsons = []

    if tags.exists():

        for tag_obj in tags:
            # Get the tag information
            tag_details = create_item_node(tag_obj)

            tags_jsons.append(tag_details)

    return tags_jsons

def leaderboards_to_json(leaderboards, current_course, post_request=None, root_json=None, messages=[]):
    ''' Converts leaderboards queryset to json '''

    leaderboards_jsons = []

    if leaderboards.exists():

        for leaderboard in leaderboards:
            # Get the leaderboard information
            leaderboard_details = create_item_node(leaderboard)

            leaderboards_jsons.append(leaderboard_details)

    return leaderboards_jsons

def content_unlocking_rules_to_json(content_unlocking_rules, current_course, post_request=None, root_json=None, messages=[]):
    ''' Converts Virtual Currency Rules to json '''
    
    content_unlocking_rules_jsons = []

    if content_unlocking_rules.exists():
       
        for content_unlocking_rule in content_unlocking_rules:
            # Get basic badge information
            content_unlocking_rule_details = create_item_node(content_unlocking_rule)

            rule = content_unlocking_rule.ruleID

            # Get the rule information
            rule_details = rule_model_to_json(rule)
            
            # Check to see if the conditions & specifier object ids are being exported as well
            if post_request:
                validate_content_unlocking_rule_json(content_unlocking_rule_details, post_request, root_json=root_json, messages=messages)

            content_unlocking_rule_details['rule'] = rule_details         

            content_unlocking_rules_jsons.append(content_unlocking_rule_details)
   
    return content_unlocking_rules_jsons

def streaks_to_json(streaks, current_course, post_request=None, root_json=None, messages=[]):
    ''' Converts streaks (AttendanceStreakConfiguration) queryset to json '''

    streaks_jsons = []

    if streaks.exists():
        
        for streak in streaks:
            # Get the streak information
            streak_details = create_item_node(streak)

            streaks_jsons.append(streak_details)

    return streaks_jsons

#############################################################
# IMPORTING
#############################################################

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')  
def importCourse(request):   
    ''' This is the main view where the import course json
        will be read
    '''

    context_dict, current_course = initialContextDict(request)
       
    if request.method == 'GET':
        return render(request,'Instructors/CourseImport.html', context_dict)
    
    if request.method == 'POST':
        if 'course' in request.FILES:
            response = {}

            # Holds the messages to display for the user in the frontend
            messages = []

            course_json = request.FILES['course']
            root_json = {}
            
            uploaded_file = UploadedFiles() 
            uploaded_file.uploadedFile = course_json     
            uploaded_file.uploadedFileName = course_json.name
            uploaded_file.uploadedFileCreator = request.user
            uploaded_file.save()

            # It is important we use uploaded_file.uploadedFile.name because
            # if there are two files with the same name, the file will
            # get renamed. This includes the rename
            with zipfile.ZipFile(uploaded_file.uploadedFile.name) as zip_file:
                with zip_file.open('course.json') as import_stream:
                    root_json = json.load(import_stream)

                if root_json:

                    id_map = initialize_id_map(root_json)

                    if 'activities' in root_json:
                        # Notify user about fields not being exported 
                        messages.append({'type': 'info', 'message': 'Activities Display From, Display To, and Due Date fields was not set after importing'})

                    if 'serious-challenges' in root_json or 'warmup-challenges' in root_json:
                        # Notify user about field export decisions
                        messages.append({'type': 'info', 'message': 'Challenges Display From, Display To, and Due Date was set to Course Start Date, Course End Date, and Course End Date respectively'})
                    
                    if 'topics' in root_json:
                        import_topics_from_json(root_json['topics'], current_course, id_map=id_map, messages=messages)

                    if 'activities-categories' in root_json:
                        import_activities_categories_from_json(root_json['activities-categories'], current_course, id_map=id_map, messages=messages)
                        
                    if 'skills' in root_json:
                        import_course_skills_from_json(root_json['skills'], current_course, id_map=id_map, messages=messages)

                    if 'activities' in root_json:
                        import_activities_from_json(root_json['activities'], current_course, id_map=id_map, messages=messages)
                    
                    if 'serious-challenges' in root_json:
                        import_challenges_from_json(root_json['serious-challenges'], current_course, context_dict=context_dict, id_map=id_map, messages=messages)
                    
                    if 'warmup-challenges' in root_json:
                        import_challenges_from_json(root_json['warmup-challenges'], current_course, context_dict=context_dict, id_map=id_map, messages=messages)
                    
                    if 'unassigned-problems' in root_json:
                        unassigned_challenge = Challenges.objects.get(courseID=current_course, challengeName=unassigned_problems_challenge_name)
                        import_challenge_questions_from_json(root_json['unassigned-problems'], unassigned_challenge, current_course, context_dict=context_dict, id_map=id_map, messages=messages)
                    
                    if 'automatic-badges' in root_json:
                        import_badges_from_json(root_json['automatic-badges'], 'automatic', current_course, id_map=id_map, messages=messages)
                
                    if 'manual-badges' in root_json:
                        import_badges_from_json(root_json['manual-badges'], 'manual', current_course, id_map=id_map, messages=messages)
                    
                    if 'periodic-badges' in root_json:
                        import_badges_from_json(root_json['periodic-badges'], 'periodic', current_course, id_map=id_map, messages=messages)
                    
                    if 'automatic-vc-rules' in root_json:
                        import_vc_rules_from_json(root_json['automatic-vc-rules'], 'automatic', current_course, id_map=id_map, messages=messages)
                    
                    if 'manual-vc-rules' in root_json:
                        import_vc_rules_from_json(root_json['manual-vc-rules'], 'manual', current_course, id_map=id_map, messages=messages)
                    
                    if 'periodic-vc-rules' in root_json:
                        import_vc_rules_from_json(root_json['periodic-vc-rules'], 'periodic', current_course, id_map=id_map, messages=messages)
                    
                    if 'spending-vc-rules' in root_json:
                        import_vc_rules_from_json(root_json['spending-vc-rules'], 'spending', current_course, id_map=id_map, messages=messages)

                    if 'leaderboards' in root_json:
                        import_leaderboards_from_json(root_json['leaderboards'], current_course, id_map=id_map, messages=messages)

                    if 'content-unlocking' in root_json:
                        import_content_unlocking_rules_from_json(root_json['content-unlocking'], current_course, id_map=id_map, messages=messages)

                    if 'streaks' in root_json:
                        import_streaks_from_json(root_json['streaks'], current_course, id_map=id_map, messages=messages)                    
                    
                else:
                    messages.append({'type': 'error', 'message': 'File: {} is empty or cannot be read'.format(uploaded_file.uploadedFile.name)})

            uploaded_file.delete()  

            # Get rid of duplicate messages by converting list of dicts 
            # to set of tuples then back to list of dicts
            messages = [dict(t) for t in {tuple(d.items()) for d in messages}]
            response['messages'] = messages
            
            # Debug messages
            # ensure_directory('media/textfiles/course/json/')
            # with open('media/textfiles/course/json/import-log.json', 'w') as import_stream:
            #     json.dump(messages, import_stream)

            return JsonResponse(response)
    
    return JsonResponse({'messages': [{'type': 'error', 'message': 'Error in the request for importing a course'}]})      

def initialize_id_map(root_json):
    ''' Sets up the id mapping for conditions, challenges, etc. '''

    id_map = {}
    if 'topics' in root_json:
        id_map['topics'] = {}
    if 'activities-categories' in root_json:
        id_map['activities-categories'] = {}
    if 'skills' in root_json:
        id_map['skills'] = {}
    if 'activities' in root_json:
        id_map['activities'] = {}
    if 'serious-challenges' in root_json:
        id_map['serious-challenges'] = {}
    if 'warmup-challenges' in root_json:
        id_map['warmup-challenges'] = {}
    if 'code-paths' in root_json:
        id_map['code-paths'] = {}

    return id_map

#############################################################
# IMPORTING JSON METHODS
#############################################################

def import_topics_from_json(topics_jsons, current_course, context_dict=None, id_map=None, messages=[]):
    ''' Converts topic jsons to model '''

    if topics_jsons:
        for topic_json in topics_jsons:

            # Create a new topic       
            topic = create_model_instance(Topics, topic_json)           
            topic.save()

            course_topics = CoursesTopics.objects.filter(topicID__topicName=topic.topicName, courseID=current_course)
            # The imported topic is the same for this course
            if course_topics:  
                course_topic = course_topics.first()                    
            else:
                # Create a new course topic
                course_topic_fields_to_save = {'topicID': topic, 'courseID': current_course}
                course_topic = create_model_instance(CoursesTopics, None, custom_fields_to_save=course_topic_fields_to_save)                                    
                course_topic.save()
            
            # Map the imported topic id to the new topic id
            if id_map:
                id_map['topics'][topic_json['topicID']] = course_topic.topicID.topicID

def import_activities_categories_from_json(activities_categories_jsons, current_course, context_dict=None, id_map=None, messages=[]):
    ''' Converts activity category jsons to model '''

    if activities_categories_jsons:
        for activities_categories_json in activities_categories_jsons:
            activities_categories = ActivitiesCategory.objects.filter(name=activities_categories_json['name'], courseID=current_course)

            # The imported activity category has the same name as one in this course
            if activities_categories:
                activity_category = activities_categories.first()
            else:
                # Create a new activity category
                activity_category_fields_to_save = {'courseID': current_course}
                activity_category = create_model_instance(ActivitiesCategory, activities_categories_json, custom_fields_to_save=activity_category_fields_to_save)
                activity_category.save()

            # Map the imported activity category id to the new activity category id
            if id_map:
                id_map['activities-categories'][activities_categories_json['categoryID']] = activity_category.categoryID

def import_course_skills_from_json(skills_jsons, current_course, context_dict=None, id_map=None, messages=[]):
    ''' Converts skill jsons to model '''

    if skills_jsons:
        for skill_json in skills_jsons:

            # skills = Skills.objects.filter(skillName=skill_json['skillName'])
            # # The imported skill has the same name of one of the skills in oneup system
            # if skills:
            #     skill = skills.first()
            # else: 

            # Create a new skill
            skill = create_model_instance(Skills, skill_json)                 
            skill.save()


            course_skills = CoursesSkills.objects.filter(skillID__skillName=skill.skillName, courseID=current_course)
            # The imported skill is the same for this course
            if course_skills:  
                course_skill = course_skills.first()     
            else:
                # Create a new course skill
                course_skill_fields_to_save = {'skillID': skill, 'courseID': current_course}
                course_skill = create_model_instance(CoursesSkills, None, custom_fields_to_save=course_skill_fields_to_save)                  
                course_skill.save()
            
            # Map the imported skill id to the new skill id
            if id_map:
                id_map['skills'][skill_json['skillID']] = course_skill.skillID.skillID

def import_activities_from_json(activities_jsons, current_course, context_dict=None, id_map=None, messages=[]):
    ''' Converts activity jsons to model '''

    if activities_jsons:
        for activity_json in activities_jsons:
            # Create the activity model instance
            activity_fields_to_save = {
                'courseID': current_course,
                'hasStartTimestamp': False,
                'hasEndTimestamp': False,
                'hasDeadline': False,
            }
            activity = create_model_instance(Activities, activity_json, custom_fields_to_save=activity_fields_to_save)
            
            uncategorized_activity_category = ActivitiesCategory.objects.get(name=uncategorized_activity, courseID=current_course)

            # Setup category for this activity
            if 'category' in activity_json:
                if id_map:
                    # Get the new category id we created by looking it up in the mapped ids dict
                    mapped_activity_category_id = search_for_mapped_id('activities-categories', activity_json['category']['categoryID'], id_map=id_map)
                    if not mapped_activity_category_id:
                        messages.append({'type': 'warn', 'message': 'Unable to find activity category id in mapped ids dictionary for activity. Activities will not include this category'})
                        # Try to assign this activity to the uncategorized activity
                        if not uncategorized_activity_category:
                            activity.delete()
                            return
                        else:
                            activity.category = uncategorized_activity_category
                            activity.save()

                        continue

                    # Set the activity category
                    activity_category = ActivitiesCategory.objects.get(categoryID=mapped_activity_category_id, courseID=current_course)
                    activity.category = activity_category
                else:
                    messages.append({'type': 'error', 'message': 'Unable to add activity categories to activities. id map not providied'})
            else:
                # Include the default uncategorized activity category
                if not uncategorized_activity_category:
                    messages.append({'type': 'error', 'message': 'Your Course does not have a uncategorized activity category. Activities will not include this category'})
                    activity.delete()
                    return

                activity.category = uncategorized_activity_category

            activity.save()

            # Map the imported activity id to the new activity id
            if id_map:
                id_map['activities'][activity_json['activityID']] = activity.activityID

def import_challenges_from_json(challenges_jsons, current_course, context_dict=None, id_map=None, messages=[]):
    ''' Converts challenge jsons to model '''

    if challenges_jsons:
        for challenge_json in challenges_jsons:
            # Use course config params to set the challenge
            # start, end, and due date to course start date,
            # course end date, and course end date respectively
            course_config_params = None
            if context_dict:
                course_config_params = context_dict['ccparams']            
            else:
                messages.append({'type': 'error', 'message': 'Couse Configuration not provided. Challenge will not be imported'})
                return

            # Create the challenge model instance
            challenge_fields_to_save = {'hasStartTimestamp': False,
                                        'hasEndTimestamp': False,
                                        'hasDueDate': False,
                                        'courseID': current_course}
            challenge = create_model_instance(Challenges, challenge_json, custom_fields_to_save=challenge_fields_to_save)

            challenge.save()

            # Create the challenge tags if any
            for tag_json in challenge_json['tags']:
                tag_fields_to_save = {
                    'tagID': Tags.objects.get(pk=tag_json['tagID']),
                    'challengeID': challenge,
                }
                challenge_tag = create_model_instance(ChallengeTags, None, custom_fields_to_save=tag_fields_to_save)
                challenge_tag.save()

            # Map the imported challenge id to the new challenge id
            if id_map:
                if challenge.isGraded:
                    id_map['serious-challenges'][challenge_json['challengeID']] = challenge.challengeID
                else:
                    id_map['warmup-challenges'][challenge_json['challengeID']] = challenge.challengeID

            # Import the challenge questions
            import_challenge_questions_from_json(challenge_json['challenge-questions'], challenge, current_course, context_dict=context_dict, id_map=id_map)

            if 'topics' in challenge_json:
                if id_map:
                    for topic in challenge_json['topics']:                        
                        # Get the new topic id we created by looking it up in the mapped ids dict
                        mapped_topic_id = search_for_mapped_id('topics', topic['topicID'], id_map=id_map)
                        if not mapped_topic_id:
                            messages.append({'type': 'warn', 'message': 'Unable to find topic id in mapped ids dictionary for challenge. Challenges will not include this topic'})
                            continue

                        # We can go straight to Topics instead of Course Topics since we have mapped it
                        # to Topics
                        topic = Topics.objects.get(topicID=mapped_topic_id)
                        if not topic:
                            messages.append({'type': 'warn', 'message': 'New topic object was not created. Challenges will not include this topic'})
                            continue

                        challenge_topic_fields_to_save = {'topicID': topic, 'challengeID': challenge}         
                        challenge_topic = create_model_instance(ChallengesTopics, None, custom_fields_to_save=challenge_topic_fields_to_save)
                        challenge_topic.save()                
                else:
                    messages.append({'type': 'error', 'message': 'Unable to add topics to challenges. id map not providied'})
            else:
                # Assigned this challenge the default unspecified topic
                course_topic = CoursesTopics.objects.get(courseID=current_course, topicID__topicName=unspecified_topic_name)
                
                if not course_topic:
                    messages.append({'type': 'error', 'message': 'Your Course does not have a unspecified topic. Challenges will not include this topic'})
                    return

                challenge_topic_fields_to_save = {'topicID': course_topic.topicID, 'challengeID': challenge}       
                challenge_topic = create_model_instance(ChallengesTopics, None, custom_fields_to_save=challenge_topic_fields_to_save)
                challenge_topic.save()

def import_challenge_questions_from_json(challenge_question_jsons, challenge, current_course, context_dict=None, id_map=None, messages=[]):
    ''' Converts challenge question jsons to model '''

    if challenge_question_jsons:
        for challenge_question_json in challenge_question_jsons:
            # Create the challenge question model instance
            challenge_question = create_model_instance(ChallengesQuestions, challenge_question_json)
            
            question_json = challenge_question_json['question']

            # Find the question type
            question_type = QuestionTypes.questionTypes[question_json['type']]['index']

            if question_type == QuestionTypes.dynamic:
                question_type_model = DynamicQuestions
            elif question_type == QuestionTypes.templatedynamic:
                question_type_model = TemplateDynamicQuestions
            else:
                question_type_model = StaticQuestions

            # Create the generic question
            question = create_model_instance(question_type_model, question_json)

            if question_type == QuestionTypes.dynamic or question_type == QuestionTypes.templatedynamic:
                dynamic_question_json = question_json['dynamic-question']

                # Modify the question to add the dynamic question fields
                question = create_model_instance(question, dynamic_question_json, modify=True)

                if question_type == QuestionTypes.templatedynamic:

                    if 'template-dynamic-question' in dynamic_question_json:
                        template_dynamic_question_json = dynamic_question_json['template-dynamic-question']

                        # Modify the question to add the template dynamic question fields
                        question = create_model_instance(question, template_dynamic_question_json, modify=True)
                        question.save()

                        # Create the template text parts
                        if 'template-text-parts' in template_dynamic_question_json:

                            for template_text_part_json in template_dynamic_question_json['template-text-parts']:
                                template_text_part_fields_to_save = {'dynamicQuestion': question}
                                template_text_part = create_model_instance(TemplateTextParts, template_text_part_json, custom_fields_to_save=template_text_part_fields_to_save)
                                template_text_part.save()
                        else:
                            messages.append({'type': 'error', 'message': 'Template Dynamic Question does not have any template text parts'})

                    else:
                        messages.append({'type': 'error', 'message': 'Tempalte Dynamic Question is not valid'})

                else:
                    question.save()

                # Create QuestionProgrammingFiles if any
                if 'question-programming-files' in dynamic_question_json and context_dict:
                    # Map the imported question id to the new question id
                    if id_map:
                        id_map['code-paths'][question_json['questionID']] = str(question.questionID)

                    for question_programming_files_json in dynamic_question_json['question-programming-files']:
                        # Get the user
                        user = User.objects.get(username=context_dict['username'])
                        
                        question_programming_files_fields_to_save = {'questionID': question, 'programmingFileUploader': user, 'programmingFileFolderName': question.questionID}
                        question_programming_file = create_model_instance(QuestionProgrammingFiles, question_programming_files_json, custom_fields_to_save=question_programming_files_fields_to_save)
                        question_programming_file.save() 

                        # Move the folder from the zip to server lua/problems directory
                        zip_folder = os.path.join("lua/problems", question_json['questionID'])
                        destination = os.path.join(LUA_PROBLEMS_ROOT, id_map['code-paths'][question_json['questionID']])
                        copy_tree(zip_folder, destination)

                # Create QuestionLibraries if any
                if 'question-libraries' in dynamic_question_json:

                    for question_library_json in dynamic_question_json['question-libraries']:
                        # Get the lua library and link it to the question
                        lua_library = LuaLibrary.objects.get(libarayName=question_library_json['libraryName'])

                        question_library_fields_to_save = {'question': question, 'library': lua_library}
                        question_library = create_model_instance(QuestionLibrary, None, custom_fields_to_save=question_library_fields_to_save)
                        question_library.save() 
            else:
                # Question type is static questions
                static_question_json = question_json['static-question']

                question = create_model_instance(question, static_question_json, modify=True)
                question.save()

                if 'answers' in static_question_json:

                    for answer_json in static_question_json['answers']:

                        static_question_answers_fields_to_save = {'questionID': question}
                        static_question_answer = create_model_instance(Answers, answer_json, custom_fields_to_save=static_question_answers_fields_to_save)
                        static_question_answer.save()

                        # Create the correct answer if this is the correct answer of the question
                        if 'correctAnswer' in answer_json:
                            correct_answers_fields_to_save = {'answerID': static_question_answer, 'questionID': question}
                            correct_answer = create_model_instance(CorrectAnswers, None, custom_fields_to_save=correct_answers_fields_to_save)
                            correct_answer.save()
                        
                        # Create matching answers if any
                        if 'matchingAnswerText' in answer_json:
                            matching_answers_fields_to_save = {'answerID': static_question_answer, 'questionID': question}
                            matching_answer = create_model_instance(MatchingAnswers, answer_json, custom_fields_to_save=matching_answers_fields_to_save)
                            matching_answer.save()
                else:
                    messages.append({'type': 'error', 'message': 'Static Question does not have any answers'})

            # Create the question tags if any
            for tag_json in question_json['tags']:
                tag_fields_to_save = {
                    'tagID': Tags.objects.get(pk=tag_json['tagID']),
                    'questionID': question,
                }
                question_tag = create_model_instance(ResourceTags, None, custom_fields_to_save=tag_fields_to_save)
                question_tag.save()

            # Create question skills if any
            if 'skills' in question_json:
                if id_map:
                    for question_skill_json in question_json['skills']:                        
                        # Get the new skill id we created by looking it up in the mapped ids dict
                        mapped_skill_id = search_for_mapped_id('skills', question_skill_json['skillID'], id_map=id_map)
                        if not mapped_skill_id:
                            messages.append({'type': 'warn', 'message': 'Unable to find skill id in mapped ids dictionary for challenge question. Challenge questions will not include this skill'})
                            continue

                        # We can go straight to Skills instead of Course Skills since we have mapped it
                        # to Skills
                        skill = Skills.objects.get(skillID=mapped_skill_id)
                        if not skill:
                            messages.append({'type': 'warn', 'message': 'New skill object was not created. Challenge questions will not include this skill'})
                            continue

                        question_skill_fields_to_save = {'skillID': skill, 'questionID': question, 'courseID': current_course}
                        question_skill = create_model_instance(QuestionsSkills, question_skill_json, custom_fields_to_save=question_skill_fields_to_save)
                        question_skill.save()                
                else:
                    messages.append({'type': 'error', 'message': 'Unable to add skills to challenge questions. id map not providied'})

            # Save the challenge question
            challenge_question_fields_to_modify = {'challengeID': challenge, 'questionID': question}
            challenge_question = create_model_instance(challenge_question, None, custom_fields_to_save=challenge_question_fields_to_modify, modify=True)
            challenge_question.save()

def update_object_specifier_json(object_specifier_json, object_type, id_map=None, messages=[]):
    ''' Updates object specifier json object ids (challenges, activities, topics, activitycategory)
        with the new mapped object ids
    '''

    def create_replaced_id_list(section, old_list):
        ''' Helper method to replace all the ids of a list with the mapped ids from id_map '''

        mapped_object_ids = []
        for object_id in old_list:
            # Find the mapped id
            mapped_object_id = search_for_mapped_id(section, int(object_id), id_map=id_map)
            
            if not mapped_object_id:
                # Unable to find id in section
                return None

            mapped_object_ids.append(mapped_object_id)

        # Return replaced old ids with new list of ids that were mapped
        return mapped_object_ids

    # Object specifier is [] or None
    if not object_specifier_json:
        return object_specifier_json

    if object_type == ObjectTypes.none:
        pass
    elif object_type == ObjectTypes.challenge:
        for specifier in object_specifier_json:
            if not specifier['value']:
                continue

            if specifier['specifier'] == 'id':
                if 'serious-challenges' not in id_map and 'warmup-challenges' not in id_map:
                    messages.append({'type': 'warn', 'message': 'Challenge Object Specifier challenge ids were not found. Challenge Specifier will be empty'})
                    specifier['value'] = []
                    continue

                # Get the new mapped ids
                mapped_object_ids = create_replaced_id_list('serious-challenges', specifier['value'])

                if not mapped_object_ids:
                    mapped_object_ids = create_replaced_id_list('warmup-challenges', specifier['value'])

                    if not mapped_object_ids:
                        messages.append({'type': 'warn', 'message': 'Unable to find challenge id in mapped ids dictionary. Challenge Specifier will be empty'})
                        specifier['value'] = []
                        continue

                # Replace old ids with new list of ids that were mapped
                specifier['value'] = mapped_object_ids

            elif specifier['specifier'] == 'topic':
                if 'topics' not in id_map:
                    messages.append({'type': 'warn', 'message': 'Challenge Object Specifier topic ids were not found. Make sure topics were exported. Challenge Specifier will be empty'})
                    specifier['value'] = []
                    continue
                
                # Get the new mapped ids
                mapped_object_ids = create_replaced_id_list('topics', specifier['value'])
                    
                if not mapped_object_ids:
                    messages.append({'type': 'warn', 'message': 'Unable to find topic id in mapped ids dictionary. Challenge Specifier will be empty'})
                    specifier['value'] = []
                    continue

                # Replace old ids with new list of ids that were mapped
                specifier['value'] = mapped_object_ids
        
    elif object_type == ObjectTypes.activity:
        for specifier in object_specifier_json:
            if not specifier['value']:
                continue

            if specifier['specifier'] == 'id':
                if 'activities' not in id_map:
                    messages.append({'type': 'warn', 'message': 'Activity Object Specifier activity ids were not found. Make sure activities were exported. Activity Specifier will be empty'})
                    specifier['value'] = []
                    continue

                # Get the new mapped ids
                mapped_object_ids = create_replaced_id_list('activities', specifier['value'])

                if not mapped_object_ids:
                    messages.append({'type': 'warn', 'message': 'Unable to find activity id in mapped ids dictionary. Activity Specifier will be empty'})
                    specifier['value'] = []
                    continue

                # Replace old ids with new list of ids that were mapped
                specifier['value'] = mapped_object_ids

            elif specifier['specifier'] == 'category':
                if 'activities-categories' not in id_map:
                    messages.append({'type': 'warn', 'message': 'Activity Object Specifier activity categories ids were not found. Make sure activities categories were exported. Activity Specifier will be empty'})
                    specifier['value'] = []
                    continue

                # Get the new mapped ids
                mapped_object_ids = create_replaced_id_list('activities-categories', specifier['value'])

                if not mapped_object_ids:
                    messages.append({'type': 'warn', 'message': 'Unable to find activity category id in mapped ids dictionary. Activity Specifier will be empty'})
                    specifier['value'] = []
                    continue

                # Replace old ids with new list of ids that were mapped
                specifier['value'] = mapped_object_ids

    elif object_type == ObjectTypes.topic:
        for specifier in object_specifier_json:
            if not specifier['value']:
                continue

            if specifier['specifier'] == 'id':
                if 'topics' not in id_map:
                    messages.append({'type': 'warn', 'message': 'Topic Object Specifier topic ids were not found. Make sure topics were exported. Topic Specifier will be empty'})
                    specifier['value'] = []
                    continue

                # Get the new mapped ids
                mapped_object_ids = create_replaced_id_list('topics', specifier['value'])
                    
                if not mapped_object_ids:
                    messages.append({'type': 'warn', 'message': 'Unable to find topic id in mapped ids dictionary. Topic Specifier will be empty'})
                    specifier['value'] = []
                    continue

                # Replace old ids with new list of ids that were mapped
                specifier['value'] = mapped_object_ids

    elif object_type == ObjectTypes.activityCategory:
        for specifier in object_specifier_json:
            if not specifier['value']:
                continue

            if specifier['specifier'] == 'id':
                if 'activities-categories' not in id_map:
                    messages.append({'type': 'warn', 'message': 'Activity Category Object Specifier activity categories ids were not found. Make sure activities categories were exported. Activity Category Specifier will be empty'})
                    specifier['value'] = []
                    continue

                # Get the new mapped ids
                mapped_object_ids = create_replaced_id_list('activities-categories', specifier['value'])

                if not mapped_object_ids:
                    messages.append({'type': 'warn', 'message': 'Unable to find activity category id in mapped ids dictionary. Activity Category Specifier will be empty'})
                    specifier['value'] = []
                    continue

                # Replace old ids with new list of ids that were mapped
                specifier['value'] = mapped_object_ids

    return object_specifier_json


# Take the mapping from conditions_utils.py and flip them
# Maps the char to the corresponding operand type
char_operand_types_map = {v: k for k, v in operand_types_to_char.items()}
# Map of exported json allOrAny to for type
for_type_map = {'ALL': 'FOR_ALL', 'ANY': 'FOR_ANY'}
# Map of object type to operand set type
object_type_map = {'activity': OperandTypes.activitySet, 'challenge': OperandTypes.challengeSet, 
                    'topic': OperandTypes.topicSet, 'category': OperandTypes.activtiyCategorySet}

def import_condition_from_json(condition_json, current_course, id_map=None, messages=[]):
    ''' Converts a condition to model '''

    if condition_json:
        if condition_json['type'] == 'ATOM':

            condition_fields_to_save = {'courseID': current_course,
                                        'operation': condition_json['op'],
                                        'operand1Type': OperandTypes.systemVariable,
                                        'operand1Value': condition_json['lhs']}

            condition = create_model_instance(Conditions, None, custom_fields_to_save=condition_fields_to_save)

            operand_2_type = condition_json['rhstype']
            
            value_to_save = condition_json['rhsvalue']

            if operand_2_type == "V" or operand_2_type == "N" or operand_2_type == "X":
                # System Variable or Immeditate Integer or Boolean
                operand_2_value = value_to_save
            elif operand_2_type == "T":
                # String Constant
                string_constant = create_model_instance(StringConstants, None, custom_fields_to_save={'stringValue': value_to_save})
                string_constant.save()
                operand_2_value = string_constant.stringID
            elif operand_2_type == "Y":
                # Date Constant
                date_constant = create_model_instance(Dates, None, custom_fields_to_save={'dateValue': date_to_selected(value_to_save, to_format='%Y-%M-%d').date()})
                date_constant.save()
                operand_2_value = date_constant.dateID

            condition_fields_to_update = {'operand2Type': char_operand_types_map[operand_2_type],
                                        'operand2Value': operand_2_value}
            # Modify condition to add the two fields
            # NOTE: operand_2_value will be converted to int before saving
            condition = create_model_instance(condition, None, custom_fields_to_save=condition_fields_to_update, modify=True)
            condition.save()

            return condition
        elif condition_json['type'] == 'AND' or condition_json['type'] == 'OR':
            # Create the condition to hold the children conditions
            condition_fields_to_save = {'courseID': current_course,
                                        'operand1Type': OperandTypes.conditionSet,
                                        'operation': condition_json['type'],
                                        'operand1Value': 0,
                                        'operand2Type': OperandTypes.noOperand,
                                        'operand2Value': 0}

            condition = create_model_instance(Conditions, condition_json, custom_fields_to_save=condition_fields_to_save)
            condition.save()
            
            # Set up condition set relationships between this condition and sub condition
            for sub_condition_json in condition_json['subConds']:
                # Create sub condition from json
                sub_condition = import_condition_from_json(sub_condition_json, current_course, id_map=id_map)
                if sub_condition:
                    condition_set_fields_to_save = {'parentCondition': condition, 'conditionInSet': sub_condition}
                    condition_set = create_model_instance(ConditionSet, None, custom_fields_to_save=condition_set_fields_to_save)
                    condition_set.save()

            return condition
        elif condition_json['type'] == 'FOR':
            # Get the operation (FOR_ALL or FOR_ANY)
            if not condition_json['allOrAny'] in for_type_map:
                messages.append({'type': 'error', 'message': 'FOR Condition type is not valid'})
                return None

            operation = for_type_map[condition_json['allOrAny']]

            if not condition_json['objectType'] in object_type_map:
                messages.append({'type': 'error', 'message': 'FOR Condition object type is not valid'})
                return None

            operand_1_type = object_type_map[condition_json['objectType']]

            if 'subCond' not in condition_json:
                messages.append({'type': 'error', 'message': 'FOR Condition does not have a sub condition'})
                return None
            
            operand_2_type = OperandTypes.condition
            operand_2_value = import_condition_from_json(condition_json['subCond'], current_course, id_map=id_map).conditionID

            condition_fields_to_save = {'courseID': current_course,
                                        'operation': operation,
                                        'operand1Type': operand_1_type,
                                        'operand1Value': not condition_json['allObjects'], # This has a not since when exported True values actually mean 0 (see conditions_utils.py)
                                        'operand2Type': operand_2_type,
                                        'operand2Value': operand_2_value}

            condition = create_model_instance(Conditions, None, custom_fields_to_save=condition_fields_to_save)
            condition.save()

            if 'objects' in condition_json and condition_json['objects']:

                if condition.operand1Type == OperandTypes.activitySet:
                    # Create the activity set for each object id
                    for activity_id in condition_json['objects']:
                        mapped_activity_id = search_for_mapped_id('activities', int(activity_id), id_map=id_map)
                        if not mapped_activity_id:
                            messages.append({'type': 'error', 'message': 'Unable to find activity id in mapped ids dictionary for conditions'})
                            continue

                        activity_set_fields_to_save = {'activity_id': mapped_activity_id, 'condition': condition}
                        activity_set = create_model_instance(ActivitySet, None, custom_fields_to_save=activity_set_fields_to_save)
                        activity_set.save()

                elif condition.operand1Type == OperandTypes.challengeSet:
                    # Create the challenge set for each object id
                    for challenge_id in condition_json['objects']:

                        mapped_challenge_id = search_for_mapped_id('serious-challenges', int(challenge_id), id_map=id_map)
                        if not mapped_challenge_id:
                            # Try to search for id in warmup-challenges mapped section
                            mapped_challenge_id = search_for_mapped_id('warmup-challenges', int(challenge_id), id_map=id_map)
                        
                        if not mapped_challenge_id:
                            messages.append({'type': 'error', 'message': 'Unable to find challenge id in mapped ids dictionary for conditions'})
                            continue

                        challenge_set_fields_to_save = {'challenge_id': mapped_challenge_id, 'condition': condition}
                        challenge_set = create_model_instance(ChallengeSet, None, custom_fields_to_save=challenge_set_fields_to_save)
                        challenge_set.save()
                        
                elif condition.operand1Type == OperandTypes.topicSet:
                    # Create the topic set for each object id
                    for topic_id in condition_json['objects']:
                        mapped_topic_id = search_for_mapped_id('topics', int(topic_id), id_map=id_map)
                        if not mapped_topic_id:
                            messages.append({'type': 'error', 'message': 'Unable to find topic id in mapped ids dictionary for conditions'})
                            continue

                        topic_set_fields_to_save = {'topic_id': mapped_topic_id, 'condition': condition}
                        topic_set = create_model_instance(TopicSet, None, custom_fields_to_save=topic_set_fields_to_save)
                        topic_set.save()

                elif condition.operand1Type == OperandTypes.activtiyCategorySet:
                    # Create the activity category set for each object id
                    for activity_category_id in condition_json['objects']:
                        mapped_activity_category_id = search_for_mapped_id('activities-categories', int(activity_category_id), id_map=id_map)
                        if not mapped_activity_category_id:
                            messages.append({'type': 'error', 'message': 'Unable to find activity category id in mapped ids dictionary for conditions'})
                            continue

                        activity_category_set_fields_to_save = {'category_id': mapped_activity_category_id, 'condition': condition}
                        activity_category_set = create_model_instance(ActivityCategorySet, None, custom_fields_to_save=activity_category_set_fields_to_save)
                        activity_category_set.save()
                else:
                    messages.append({'type': 'error', 'message': 'FOR Condition operand 1 type is not a valid type'})
                    return None

            return condition

    return None

def import_rule_json(rule_json, current_course, id_map=None, messages=[]):
    ''' Converts a rule json to model 
        Also creates the corresponding rule events
    '''
    
    if rule_json:
        # Create the condition
        condition = import_condition_from_json(rule_json['condition'], current_course, id_map=id_map)

        if not condition:
            messages.append({'type': 'error', 'message': 'Failed to create condition(s). Some Automatic Badges, Automatic Earning Virtual Currency Rules, \
                                    and Content Unlocking Rules were not imported into the course'})
            return None

        # Update the object specifier json to include the new ids for activities, topics, challenges, categories, etc
        # And parse object specifier to string
        object_type = AwardFrequency.awardFrequency[rule_json['awardFrequency']]['objectType']
        object_specifier = json.dumps(update_object_specifier_json(rule_json['objectSpecifier'], object_type, id_map=id_map))

        rule_fields_to_save = {'courseID': current_course, 'conditionID': condition, 'objectSpecifier': object_specifier}
        rule = create_model_instance(Rules, rule_json, custom_fields_to_save=rule_fields_to_save)
        rule.save()

        # Create rule events
        events = get_events_for_condition(condition, object_type)
        for event, isGlobal in events:
            rule_event_fields_to_save = {'rule': rule, 'event': event, 'inGlobalContext': isGlobal}
            rule_event = create_model_instance(RuleEvents, None, custom_fields_to_save=rule_event_fields_to_save)
            rule_event.save()

        return rule
    
    return None

def import_badges_from_json(badges_jsons, badge_type, current_course, context_dict=None, id_map=None, messages=[]):
    ''' Converts a badge (Automatic, Manual, Periodic) to model '''

    if badges_jsons:
        for badge_json in badges_jsons:

            # Create the badge model instance for type
            if badge_type == 'automatic':
                badge_type_model = Badges
            elif badge_type == 'periodic':
                badge_type_model = PeriodicBadges
            else:
                badge_type_model = BadgesInfo

            badge_fields_to_save = {'courseID': current_course}
            badge = create_model_instance(badge_type_model, badge_json, custom_fields_to_save=badge_fields_to_save)

            if badge_type == 'automatic':
                rule_json = badge_json['rule']

                # Create the rule
                rule = import_rule_json(rule_json, current_course, id_map=id_map, messages=messages)

                # Failed to create rule so don't create the badge (error is shown in import_rule_json)
                if rule is None:
                    continue

                # Set the badge rule
                badge = create_model_instance(badge, None, custom_fields_to_save={'ruleID': rule}, modify=True)
                badge.save()

                # Create action argument for badge                
                action_argument_fields_to_save = {'ruleID': rule, 'sequenceNumber': 1, 'argumentValue': badge.badgeID}
                action_argument = create_model_instance(ActionArguments, None, custom_fields_to_save=action_argument_fields_to_save)
                action_argument.save() 

            elif badge_type == 'periodic':
                # Add the periodic fields to badge
                periodic_badge_fields_to_update = {'lastModified': current_localtime()}
                badge = create_model_instance(badge, badge_json, custom_fields_to_save=periodic_badge_fields_to_update, modify=True)
                badge.save()
                
                # Create the periodic task 
                if badge_json['periodicType'] == 0:
                    # TopN
                    badge = create_model_instance(badge, None, custom_fields_to_save={'periodicTask': setup_periodic_badge(unique_id=int(badge.badgeID), badge_id=int(badge.badgeID), variable_index=int(badge.periodicVariableID), course=current_course, period_index=int(badge.timePeriodID), number_of_top_students=int(badge.numberOfAwards), threshold=int(badge.threshold), operator_type=badge.operatorType)}, modify=True)
                elif badge_json['periodicType'] == 2:
                    # Random
                    badge = create_model_instance(badge, None, custom_fields_to_save={'periodicTask': setup_periodic_badge(unique_id=int(badge.badgeID), badge_id=int(badge.badgeID), variable_index=int(badge.periodicVariableID), course=current_course, period_index=int(badge.timePeriodID), threshold=int(badge.threshold), operator_type=badge.operatorType, is_random=badge.isRandom)}, modify=True)
                else:
                    # All (1)
                    badge = create_model_instance(badge, None, custom_fields_to_save={'periodicTask': setup_periodic_badge(unique_id=int(badge.badgeID), badge_id=int(badge.badgeID), variable_index=int(badge.periodicVariableID), course=current_course, period_index=int(badge.timePeriodID), threshold=int(badge.threshold), operator_type=badge.operatorType)}, modify=True)
                badge.save()
            else:
                # Badge is manual
                badge.save()

def import_vc_rules_from_json(vc_rules_jsons, vc_rule_type, current_course, id_map=None, messages=[]):
    ''' Converts a virtual currency rule (Automatic, Manual, Periodic, Spending) to model '''

    if vc_rules_jsons:
        for vc_rule_json in vc_rules_jsons:

            # Create the vc rule model instance for type
            if vc_rule_type == 'automatic' or vc_rule_type == 'spending':
                vc_rule_type_model = VirtualCurrencyRuleInfo
            elif vc_rule_type == 'periodic':
                vc_rule_type_model = VirtualCurrencyPeriodicRule
            else:
                vc_rule_type_model = VirtualCurrencyCustomRuleInfo
            
            vc_rule_fields_to_save = {'courseID': current_course}
            vc_rule = create_model_instance(vc_rule_type_model, vc_rule_json, custom_fields_to_save=vc_rule_fields_to_save)

            if vc_rule_type == 'automatic':
                rule_json = vc_rule_json['rule']

                # Create the rule
                rule = import_rule_json(rule_json, current_course, id_map=id_map, messages=messages)

                # Failed to create rule so don't create the vc rule (error is shown in import_rule_json)
                if rule is None:
                    continue

                # Set the vc rule to include new rule
                vc_rule = create_model_instance(vc_rule, None, custom_fields_to_save={'ruleID': rule}, modify=True)
                vc_rule.save()

                # Create action argument for vc rule
                # NOTE: Argument value is set to same as when saving virtual currency earning rule (see saveVirtualCurrencyRule.py)
                # if this value is changed, it needs to be updated here as well
                action_argument_fields_to_save = {'ruleID': rule, 'sequenceNumber': 1, 'argumentValue': rule_json['vcRuleAmount']}
                action_argument = create_model_instance(ActionArguments, None, custom_fields_to_save=action_argument_fields_to_save)
                action_argument.save() 

            elif vc_rule_type == 'periodic':
                # Add the periodic fields to vc rule
                periodic_vc_rule_fields_to_update = {'lastModified': current_localtime()}
                vc_rule = create_model_instance(vc_rule, vc_rule_json, custom_fields_to_save=periodic_vc_rule_fields_to_update, modify=True)
                vc_rule.save()
                
                # Create the periodic task 
                if vc_rule_json['periodicType'] == 0:
                    # TopN
                    vc_rule = create_model_instance(vc_rule, None, custom_fields_to_save={'periodicTask', setup_periodic_vc(unique_id=int(vc_rule.vcRuleID), virtual_currency_amount=int(vc_rule.vcRuleAmount), variable_index=int(vc_rule.periodicVariableID), course=current_course, period_index=int(vc_rule.timePeriodID), number_of_top_students=int(vc_rule.numberOfAwards), threshold=int(vc_rule.threshold), operator_type=vc_rule.operatorType)}, modify=True)
                elif vc_rule_json['periodicType'] == 2:
                    # Random
                    vc_rule = create_model_instance(vc_rule, None, custom_fields_to_save={'periodicTask', setup_periodic_vc(unique_id=int(vc_rule.vcRuleID), virtual_currency_amount=int(vc_rule.vcRuleAmount), variable_index=int(vc_rule.periodicVariableID), course=current_course, period_index=int(vc_rule.timePeriodID), threshold=int(vc_rule.threshold), operator_type=vc_rule.operatorType, is_random=vc_rule.isRandom)}, modify=True)
                else:
                    # All (1)
                    vc_rule = create_model_instance(vc_rule, None, custom_fields_to_save={'periodicTask': setup_periodic_vc(unique_id=int(vc_rule.vcRuleID), virtual_currency_amount=int(vc_rule.vcRuleAmount), variable_index=int(vc_rule.periodicVariableID), course=current_course, period_index=int(vc_rule.timePeriodID), threshold=int(vc_rule.threshold), operator_type=vc_rule.operatorType)}, modify=True)
                
                vc_rule.save()
            elif vc_rule_type == 'spending':
                # Create the default spending condition
                condition_fields_to_save = {'operation': '=', 'operand1Type': OperandTypes.immediateInteger,
                                            'operand1Value': 1, 'operand2Type': OperandTypes.immediateInteger,
                                            'operand2Value': 1, 'courseID': current_course}
                condition = create_model_instance(Conditions, None, custom_fields_to_save=condition_fields_to_save)
                condition.save()

                rule_fields_to_save = {'courseID': current_course, 'conditionID': condition, 
                                        'actionID': Action.decreaseVirtualCurrency}
                rule = create_model_instance(Rules, None, custom_fields_to_save=rule_fields_to_save)
                rule.save()

                # Create rule event
                rule_event_fields_to_save = {'rule': rule, 'event': Event.spendingVirtualCurrency}
                rule_event = create_model_instance(RuleEvents, None, custom_fields_to_save=rule_event_fields_to_save)
                rule_event.save()

                # Set the vc rule to include new rule
                vc_rule = create_model_instance(vc_rule, None, custom_fields_to_save={'ruleID': rule}, modify=True)
                vc_rule.save()

                # Create action argument for vc rule
                action_argument_fields_to_save = {'ruleID': rule, 'sequenceNumber': 1, 'argumentValue': vc_rule_json['vcRuleAmount']}
                action_argument = create_model_instance(ActionArguments, None, custom_fields_to_save=action_argument_fields_to_save)
                action_argument.save()

            else:
                # vc rule is manual
                vc_rule.save()

def import_leaderboards_from_json(leaderboards_jsons, current_course, id_map=None, messages=[]):
    ''' Converts a leaderboard to model '''

    if leaderboards_jsons:
        for leaderboard_json in leaderboards_jsons:

            # Create the leaderboard model instance
            leaderboard_fields_to_save = {'lastModified': current_localtime(), 'courseID': current_course}
            leaderboard = create_model_instance(LeaderboardsConfig, leaderboard_json, custom_fields_to_save=leaderboard_fields_to_save)
            leaderboard.save()

            # Create periodic task for leaderboard
            leaderboard = create_model_instance(leaderboard, None, custom_fields_to_save={'periodicTask': setup_periodic_leaderboard(leaderboard_id=leaderboard.leaderboardID, variable_index=leaderboard.periodicVariable, course=leaderboard.courseID, period_index=leaderboard.timePeriodUpdateInterval,  number_of_top_students=leaderboard.numStudentsDisplayed, threshold=1, operator_type='>', is_random=None)}, modify=True)
            leaderboard.save()

def import_content_unlocking_rules_from_json(content_unlocking_rules_jsons, current_course, id_map=None, messages=[]):
    ''' Converts a content unlocking rule to model '''

    if content_unlocking_rules_jsons:
        for content_unlocking_rule_json in content_unlocking_rules_jsons:

            # Create the badge model instance for type
            content_unlocking_rule_fields_to_save = {'courseID': current_course}
            content_unlocking_rule = create_model_instance(ProgressiveUnlocking, content_unlocking_rule_json, custom_fields_to_save=content_unlocking_rule_fields_to_save)

            rule_json = content_unlocking_rule_json['rule']

            # Create the rule
            rule = import_rule_json(rule_json, current_course, id_map=id_map, messages=messages)

            # Failed to create rule so don't create the content unlocking rule (error is shown in import_rule_json)
            if rule is None:
                continue

            # Set the content unlocking rule to include new rule
            content_unlocking_rule = create_model_instance(content_unlocking_rule, None, custom_fields_to_save={'ruleID': rule}, modify=True)
            content_unlocking_rule.save()

            # Create action argument for content unlocking rule
            action_argument_fields_to_save = {'ruleID': rule, 'sequenceNumber': 1, 'argumentValue': content_unlocking_rule.pk}
            action_argument = create_model_instance(ActionArguments, None, custom_fields_to_save=action_argument_fields_to_save)
            action_argument.save() 

            # Make Student objects for the content unlocking rule
            students_registered_courses = StudentRegisteredCourses.objects.filter(courseID=current_course)
            for students_registered_course in students_registered_courses:
                
                student_content_unlocking_fields_to_save = {'studentID': students_registered_course.studentID, 'pUnlockingRuleID': content_unlocking_rule,
                                                            'courseID': current_course}
                student_content_unlocking =  create_model_instance(StudentProgressiveUnlocking, content_unlocking_rule_json, custom_fields_to_save=student_content_unlocking_fields_to_save)
                student_content_unlocking.save()

def import_streaks_from_json(streaks_jsons, current_course, id_map=None, messages=[]):
    ''' Converts a streak (AttendanceStreakConfiguration) to model '''

    if streaks_jsons:
        for streak_json in streaks_jsons:
            
            # Create the streak model instance
            streaks_fields_to_save = {'courseID': current_course}
            streak = create_model_instance(AttendanceStreakConfiguration, streak_json, custom_fields_to_save=streaks_fields_to_save)
            streak.save()
