''' Created by Austin Hodge 5-18-19 '''

from django.shortcuts import redirect, render, HttpResponse
from django.http import JsonResponse

from Instructors.models import Courses, Challenges, CoursesTopics, ChallengesTopics, ChallengesQuestions, StaticQuestions 
from Instructors.models import Answers, MatchingAnswers, CorrectAnswers, UploadedFiles 
from Instructors.models import DynamicQuestions, TemplateDynamicQuestions, TemplateTextParts, QuestionLibrary, LuaLibrary, QuestionsSkills, Skills, CoursesSkills
from Instructors.models import Activities, ActivitiesCategory
from Instructors.models import Topics, CoursesTopics

from Badges.models import BadgesInfo, Badges, PeriodicBadges
from Badges.models import RuleEvents, Rules, Conditions, ActionArguments, FloatConstants, StringConstants, Dates, ConditionSet, ChallengeSet, ActivitySet, ActivityCategorySet, TopicSet
from Badges.models import VirtualCurrencyCustomRuleInfo, VirtualCurrencyRuleInfo, VirtualCurrencyPeriodicRule
from Badges.models import LeaderboardsConfig
from Badges.models import ProgressiveUnlocking
from Badges.models import AttendanceStreakConfiguration

from Students.models import StudentRegisteredCourses, StudentProgressiveUnlocking

from Badges.models import CourseConfigParams

from Badges.enums import AwardFrequency, ObjectTypes, OperandTypes, Event, Action
from Instructors.questionTypes import QuestionTypes

from Badges.conditions_util import databaseConditionToJSONString, stringAndPostDictToCondition, chosenObjectSpecifierFields, operand_types_to_char, get_events_for_condition
from Badges.periodicVariables import setup_periodic_badge, setup_periodic_vc, setup_periodic_leaderboard
from Instructors.views.utils import initialContextDict, utcDate
from Instructors.constants import unspecified_topic_name, unassigned_problems_challenge_name, uncategorized_activity

from decimal import Decimal

import os
import json

from django.contrib.auth.decorators import login_required, user_passes_test
from oneUp.settings import MEDIA_ROOT
from oneUp.decorators import instructorsCheck 


#############################################################
# HELPER METHODS
#############################################################

model_lookup_table = {
    Topics: {
        'topicName': None,
    },
    CoursesTopics: {
        'topicID': None,
        'courseID': None,
    },
    ActivitiesCategory: {
        'name': None,
        'courseID': None,
    },
    Skills: {
        'skillName': None,
    },
    CoursesSkills: {
        'skillID': None,
        'courseID': None,
    },
    Activities: {
        'activityName': None,
        'isGraded': None,
        'description': None,
        'points': Decimal,
        'isFileAllowed': None,
        'uploadAttempts': None,
        'instructorNotes': None,
        'author': None,
        'courseID': None,
    },
    Challenges: {
        'challengeName': None,
        'isGraded': None,
        'numberAttempts': None,
        'timeLimit': None,
        'displayCorrectAnswer': None,
        'displayCorrectAnswerFeedback': None,
        'displayIncorrectAnswerFeedback': None,
        'challengeAuthor': None,
        'challengeDifficulty': None,
        'challengePassword': None,
        'startTimestamp': None,
        'endTimestamp': None,
        'dueDate': None,
        'courseID': None,
    },
    ChallengesTopics: {
        'topicID': None,
        'challengeID': None,
    },
    ChallengesQuestions: {
        'points': Decimal,
        'challengeID': None,
        'questionID': None,
    }
    DynamicQuestions: {
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
    TemplateDynamicQuestions: {
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
    TemplateTextParts: {
        'partNumber': None,
        'templateText': None,
        'dynamicQuestion': None,
    },
    QuestionLibrary: {
        'question': None,
        'library': None,
    },
    StaticQuestions: {
        'preview': None,
        'instructorNotes': None,
        'type': None,
        'difficulty': None,
        'author': None,
        
        'questionText': None,
        'correctAnswerFeedback': None,
        'incorrectAnswerFeedback': None,
    },
    Answers: {
        'answerText': None,
        'questionID': None,
    },
    CorrectAnswers: {
        'answerID': None,
        'questionID': None,
    },
    MatchingAnswers: {
        'answerID': None,
        'questionID': None,
        'matchingAnswerText': None,
    },
    QuestionsSkills: {
        'skillID': None,
        'questionID': None,
        'questionSkillPoints': None,
        'courseID': None,
    },
    Conditions: {
        'courseID': None,
        'operation': None,
        'operand1Type': None,
        'operand1Value': int,
        'operand2Type': None,
        'operand2Value': int,
    },
    ConditionSet: {
        'parentCondition': None,
        'conditionInSet': None,
    },
    ActivitySet: {
        'activity_id': int,
        'condition': None,
    },
    ChallengeSet: {
        'challenge_id': int,
        'condition': None,
    },
    TopicSet: {
        'topic_id': int,
        'condition': None,
    },
    ActivityCategorySet: {
        'category_id': int,
        'condition': None,
    }
    StringConstants: {
        'stringValue': None,
    },
    Dates: {
        'dateValue': None,
    },
    Rules: {
        'courseID': None,
        'conditionID': None,
        'actionID': None,
        'objectSpecifier': None,
        'awardFrequency': None,
    },
    RuleEvents: {
        'rule': None,
        'event': None,
        'inGlobalContext': None,
    },
    Badges: {
        'badgeName': None,
        'badgeDescription': None,
        'badgeImage': None,
        'manual': None,
        'isPeriodic': None,
        'courseID': None,

        'ruleID': None,
    },
    PeriodicBadges: {
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
    BadgesInfo: {
        'badgeName': None,
        'badgeDescription': None,
        'badgeImage': None,
        'manual': None,
        'isPeriodic': None,
        'courseID': None,
    },
    ActionArguments: {
        'ruleID': None,
        'sequenceNumber': None,
        'argumentValue': str,
    },
    VirtualCurrencyRuleInfo: {
        'vcRuleName': None,
        'vcRuleDescription': None,
        'vcRuleType': None,
        'vcRuleAmount': None,
        'vcRuleLimit': None,
        'isPeriodic': None,
        'courseID': None,

        'ruleID': None,
    },
    VirtualCurrencyPeriodicRule: {
        'vcRuleName': None,
        'vcRuleDescription': None,
        'vcRuleType': None,
        'vcRuleAmount': None,
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
    VirtualCurrencyCustomRuleInfo: {
        'vcRuleName': None,
        'vcRuleDescription': None,
        'vcRuleType': None,
        'vcRuleAmount': None,
        'vcRuleLimit': None,
        'isPeriodic': None,
        'courseID': None,
    },
    LeaderboardsConfig: {
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
    ProgressiveUnlocking: {
        'name': None,
        'description': None,
        'objectID': None,
        'objectType': None,
        'courseID': None,

        'ruleID': None,
    },
    StudentProgressiveUnlocking: {
        'studentID': None,
        'pUnlockingRuleID': None,
        'courseID': None,
        'objectID': None,
        'objectType': None,
    },
    AttendanceStreakConfiguration: {
        'daysofClass': None,
        'daysDeselected': None,
        'courseID': None
    }

}

def ensure_directory(directory):
    ''' Make sure the directory exists on the server (or locally) '''

    if not os.path.exists(directory):
        os.makedirs(directory)

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

        Note: use custom_field_to_save parameter if you need to modify/create the 
        model instance with a custom value that is not in the fields_data json.
        custom_field_to_save will override field_data for the same field name.

    '''
    if modify:
        model_instance = model
        model_type = type(model)
    else:
        model_instance = model()
        model_type = model

    for field_name, cast_specifier in model_lookup_table[model_type].items():
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

    context_dict['version'] = "1.0"

    if request.method == 'GET':
        return render(request,'Instructors/CourseExport.html', context_dict)
    
    if request.method == 'POST':
        root_json = json.loads(request.POST.get('exported-json', ''))
        # Only export json if the json contains items other than the version number
        if 'version' in root_json and len(root_json) > 1:
            ensure_directory('media/textfiles/course/json/')
            with open('media/textfiles/course/json/course-{}-{}.json'.format(current_course.courseName, root_json['version']), 'w') as export_stream:
                json.dump(root_json, export_stream)

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
                messages.append({'type': 'info', 'message': 'Challenges Display From, Display To, and Due Date will not be exported. These options will be set to Course Start Date, Course End Date, and Course End Date respectively automatically'})

            post_request = dict(request.POST)

            # Versioning
            root_json['version'] = "1.0"

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
                root_json['serious-challenges'] = challenges_to_json(serious_challenges, current_course, include_topics='topics' in request.POST, messages=messages)

            if 'warmup-challenges' in request.POST:
                # Exclude unassigned challenge since that is created by default for every course
                warmup_challenges = Challenges.objects.filter(courseID=current_course, isGraded=False).exclude(challengeName=unassigned_problems_challenge_name)
                root_json['warmup-challenges'] = challenges_to_json(warmup_challenges, current_course, include_topics='topics' in request.POST, messages=messages)

            if 'unassigned-problems' in request.POST:
                unassigned_challenge = Challenges.objects.get(courseID=current_course, challengeName=unassigned_problems_challenge_name)
                challenge_questions = ChallengesQuestions.objects.filter(challengeID=unassigned_challenge)
                # Get only the challenge questions as json
                root_json['unassigned-problems'] = challenge_questions_to_json(challenge_questions, current_course, messages=messages)
            
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
                manual_vc_rules = VirtualCurrencyCustomRuleInfo.objects.filter(courseID=current_course, vcRuleType=True, isPeriodic=False)
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
        # Select what fields to save from the model
        # Second element of tuple is what to cast the model field to
        challenge_fields_to_save = [('challengeID', None), ('challengeName', None), ('isGraded', None), ('numberAttempts', None), 
                                ('timeLimit', None), ('displayCorrectAnswer', None), 
                                ('displayCorrectAnswerFeedback', None), ('displayIncorrectAnswerFeedback', None), 
                                ('challengeAuthor', None), ('challengeDifficulty', None),
                                ('challengePassword', None),]
        for challenge in challenges:
            # Get the challenge information
            challenge_details = create_item_node(challenge, challenge_fields_to_save)

            if include_topics:
                # Add topics for this challenge if any
                challenge_topics = ChallengesTopics.objects.filter(challengeID=challenge)
                if challenge_topics.exists(): 
                    # Add to challenge details
                    challenge_details['topics'] = topics_to_json(challenge_topics, current_course, messages=[])

            
            # Add questions for this challenges
            challenge_questions = ChallengesQuestions.objects.filter(challengeID=challenge)

            # Add the questions to the challenge object
            challenge_details['challenge-questions'] = challenge_questions_to_json(challenge_questions, current_course, post_request=post_request, root_json=root_json, messages=[])

            challenges_jsons.append(challenge_details)

    return challenges_jsons

def challenge_questions_to_json(challenge_questions, current_course, post_request=None, root_json=None, messages=[]):
    ''' Converts challenge questions queryset to json '''

    challenge_questions_jsons = []

    if challenge_questions.exists():
        # Cast the points field to a str after getting value from database since it is stored as Decimal
        challenge_question_fields_to_save = [('points', str),]

        for challenge_question in challenge_questions:
            # Add the challenge question model details
            challenge_question_details = create_item_node(challenge_question, challenge_question_fields_to_save)
            
            # Add the question model details
            question = challenge_question.questionID
            question_fields_to_save = [('preview', None), ('instructorNotes', None), ('type', None),
                                        ('difficulty', None), ('author', None),]
            question_details = create_item_node(question, question_fields_to_save)

            # Add the question skills if any
            question_skills = QuestionsSkills.objects.filter(questionID=question, courseID = current_course)
            if question_skills.exists():
                question_skills_jsons = []

                questions_skills_fields_to_save = [('questionSkillPoints', None),]
                skills_fields_to_save = [('skillID', None),('skillName', None),]

                for skill in question_skills: 
                    skill_details = create_item_node(skill, questions_skills_fields_to_save)
                    # Add the skill id and name
                    skill_details.update(create_item_node(skill.skillID, skills_fields_to_save))

                    question_skills_jsons.append(skill_details)

                # Add questions skills to the question model details
                question_details['skills'] = question_skills_jsons

            # Add the Static Question if it is this type
            static_questions = StaticQuestions.objects.filter(questionID=int(question.questionID))
            if static_questions.exists():
                static_question = static_questions.first()
                static_question_fields_to_save = [('questionText', None), ('correctAnswerFeedback', None), 
                                                ('incorrectAnswerFeedback', None),]
                static_question_details = create_item_node(static_question, static_question_fields_to_save)

                # Add Answers for Static Questions
                static_question_answers = Answers.objects.filter(questionID=static_question)    
                static_question_answers_jsons = []
                static_question_answers_fields_to_save = [('answerText', None),]
                for answer in static_question_answers:            
                    answer_details = create_item_node(answer, static_question_answers_fields_to_save)
                
                    # Check if it is a correct answer
                    correct_answers = CorrectAnswers.objects.filter(questionID=static_question, answerID = answer)
                    if correct_answers.exists():
                        answer_details['correctAnswer'] = "yes"
                        
                    # Check if this answer has a matching answer
                    if challenge_question.questionID.type == QuestionTypes.matching:                                               
                        matching_answer = MatchingAnswers.objects.get(answerID=answer, questionID=static_question) 
                        if matching_answer:
                            answer_details['matchingAnswerText'] = matching_answer.matchingAnswerText

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

                dynamic_question_fields_to_save = [('numParts', None), ('code', None),]
                dynamic_question_details = create_item_node(dynamic_question, dynamic_question_fields_to_save)
        
                # Add the TemplateDynamicQuestions if any
                template_dynamic_questions = TemplateDynamicQuestions.objects.filter(questionID=int(question.questionID))
                if template_dynamic_questions.exists():
                    template_dynamic_question = template_dynamic_questions.first()

                    template_dynamic_question_fields_to_save = [('templateText', None), ('setupCode', None),]
                    template_dynamic_question_details = create_item_node(template_dynamic_question, template_dynamic_question_fields_to_save)
    
                    # Add the TemplateTextParts
                    template_text_parts = TemplateTextParts.objects.filter(dynamicQuestion=question)
                    if template_text_parts.exists():                        
                        template_text_parts_jsons = []
                        template_text_parts_fields_to_save = [('partNumber', None), ('templateText', None),]
                        for part in template_text_parts:    
                            template_text_part_details = create_item_node(part, template_text_parts_fields_to_save)
                            template_text_parts_jsons.append(template_text_part_details)
                        # Add the template parts to the tempalte dyanmic question
                        template_dynamic_question_details['template-text-parts'] = template_text_parts_jsons

                    # Add template dynamic question to dynamic question
                    dynamic_question_details['template-dynamic-question'] = template_dynamic_question_details
        
                # Add QuestionLibrary if any
                question_libraries = QuestionLibrary.objects.filter(question=question)
                if question_libraries.exists():
                    question_libraries_jsons = []
                    for question_library in question_libraries:     
                        question_library_details = {}
                        question_library_details['libraryName'] = question_library.library.libraryName                 
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
        # Select what fields to save from the model
        # Second element of tuple is what to cast the model field to
        activity_fields_to_save = [('activityID', None), ('activityName', None), ('isGraded', None), ('description', None), 
                                ('points', str), ('isFileAllowed', None), 
                                ('uploadAttempts', None), ('instructorNotes', None), 
                                ('author', None),]
        for activity in activities:
            # Get the activity information
            activity_details = create_item_node(activity, activity_fields_to_save)

            # Note: we are also including Uncategorized category just in case to map the id  
            # if it has been used in conditions rules
            if include_categories:
                # Save the activity category
                activity_details['category'] = create_item_node(activity.category, [('categoryID', None), ('name', None),])

            # Add the activity details to the activities json list
            activities_jsons.append(activity_details)

    return activities_jsons

def activities_categories_to_json(activities_categories, current_course, post_request=None, root_json=None, messages=[]):
    ''' Converts Activity Categories queryset to json '''

    activities_categories_jsons = []

    if activities_categories.exists(): 
        activity_category_fields_to_save = [('categoryID', None), ('name', None),]
        for category in activities_categories:
            # Note: we are also including Uncategorized category just in case to map the id  
            # if it has been used in conditions rules
            
            # Get category information
            activity_category_details = create_item_node(category, activity_category_fields_to_save)
            
            activities_categories_jsons.append(activity_category_details)

    return activities_categories_jsons

def badges_to_json(badges, badge_type, current_course, post_request=None, root_json=None, messages=[]):
    ''' Converts Badges queryset to json '''
    
    badges_jsons = []

    if badges.exists():
        badges_fields_to_save = [('badgeName', None), ('badgeDescription', None), ('badgeImage', None), 
                                ('manual', None), ('isPeriodic', None),]
        for badge in badges:
            # Get basic badge information
            badge_details = create_item_node(badge, badges_fields_to_save)

            if badge_type == 'automatic':
                automatic_badge_rule = badge.ruleID

                # Get the badge rule details
                automatic_badge_rule_details = rule_model_to_json(automatic_badge_rule, post_request=post_request, root_json=root_json, messages=messages)

                badge_details['rule'] = automatic_badge_rule_details

            elif badge_type == 'periodic':
                # Add periodic badge details to badge details
                perioidc_badge_details = periodic_model_to_json(badge)

                badge_details.update(perioidc_badge_details)
            

            badges_jsons.append(badge_details)

    return badges_jsons

def vc_rules_to_json(vc_rules, vc_rule_type, current_course, post_request=None, root_json=None, messages=[]):
    ''' Converts Virtual Currency Rules to json '''
    
    vc_rules_jsons = []

    if vc_rules.exists():
        vc_rule_fields_to_save = [('vcRuleName', None), ('vcRuleDescription', None), ('vcRuleType', None), 
                                ('vcRuleAmount', None), ('vcRuleLimit', None), ('isPeriodic', None),]
        for vc_rule in vc_rules:
            # Get basic badge information
            vc_rule_details = create_item_node(vc_rule, vc_rule_fields_to_save)

            if vc_rule_type == 'automatic':
                automatic_vc_rule = vc_rule.ruleID

                # Get the vc rule details
                automatic_vc_rule_details = rule_model_to_json(automatic_vc_rule, post_request=post_request, root_json=root_json, messages=messages)

                vc_rule_details['rule'] = automatic_vc_rule_details
            
            elif vc_rule_type == 'periodic':
                # Add periodic vc rule details to vc rule details
                perioidc_vc_rule_details = periodic_model_to_json(vc_rule)

                vc_rule_details.update(perioidc_vc_rule_details)            

            vc_rules_jsons.append(vc_rule_details)

    return vc_rules_jsons

def rule_model_to_json(automatic_rule, automatic_rule_fields_to_save=[('actionID', None), ('awardFrequency', None),], post_request=None, root_json=None, messages=[]):
    ''' Converts a Rule to json '''

    if automatic_rule:
        # Get the rule information
        automatic_rule_details = create_item_node(automatic_rule, automatic_rule_fields_to_save)

        # Setup Object specifier
        automatic_rule_object_specifier = automatic_rule.objectSpecifier
        automatic_rule_details['objectSpecifier'] = json.loads(automatic_rule_object_specifier)
        # Get the rule condition string
        automatic_rule_condition = automatic_rule.conditionID
        automatic_rule_details['condition'] = json.loads(databaseConditionToJSONString(automatic_rule_condition))

        # Check to see if the conditions & specifier object ids are being exported as well
        if post_request:
            validate_rule_json(automatic_rule_details, post_request, root_json=root_json, messages=messages)

        return automatic_rule_details

    return None

def periodic_model_to_json(periodic_object, periodic_fields_to_save=[('periodicVariableID', None), ('timePeriodID', None),
                                    ('periodicType', None), ('numberOfAwards', None),
                                    ('threshold', None), ('operatorType', None), 
                                    ('isRandom', None), ('resetStreak', None),]):

    ''' Takes a periodic query that is instance of a periodic model:
        PeriodicBadges, VirtualCurrencyPeriodicRule
    '''

    return create_item_node(periodic_object, periodic_fields_to_save)

def topics_to_json(topics, current_course, post_request=None, root_json=None, messages=[]):
    ''' Converts topics (Course Topics or Challenge Topics) queryset to json '''

    topics_jsons = []

    if topics.exists():
        topics_fields_to_save = [('topicID', None), ('topicName', None),]
        for course_topic in topics:
            # Note: we are also including Unspecified topic just in case to map the id 
            # if it has been used in conditions rules

            topic = course_topic.topicID
            # Get the topic information
            topic_details = create_item_node(topic, topics_fields_to_save)

            topics_jsons.append(topic_details)

    return topics_jsons

def course_skills_to_json(course_skills, current_course, post_request=None, root_json=None, messages=[]):
    ''' Converts skills (CoursesSkills) queryset to json '''

    course_skills_jsons = []

    if course_skills.exists():
        skills_fields_to_save = [('skillID', None), ('skillName', None),]
        for course_skill in course_skills: 
            skill = course_skill.skillID
            # Get the skills details into json
            skill_details = create_item_node(skill, skills_fields_to_save)
            # Add to json list
            course_skills_jsons.append(skill_details)

    return course_skills_jsons

def leaderboards_to_json(leaderboards, current_course, post_request=None, root_json=None, messages=[]):
    ''' Converts leaderboards queryset to json '''

    leaderboards_jsons = []

    if leaderboards.exists():
        leaderboards_fields_to_save = [('leaderboardName', None), ('leaderboardDescription', None),
                                        ('isContinous', None),('isXpLeaderboard', None), ('numStudentsDisplayed', None),
                                        ('periodicVariable', None), ('timePeriodUpdateInterval', None), 
                                        ('displayOnCourseHomePage', None), ('howFarBack', None),]
        for leaderboard in leaderboards:
            # Get the leaderboard information
            leaderboard_details = create_item_node(leaderboard, leaderboards_fields_to_save)

            leaderboards_jsons.append(leaderboard_details)

    return leaderboards_jsons

def content_unlocking_rules_to_json(content_unlocking_rules, current_course, post_request=None, root_json=None, messages=[]):
    ''' Converts Virtual Currency Rules to json '''
    
    content_unlocking_rules_jsons = []

    if content_unlocking_rules.exists():
        content_unlocking_rule_fields_to_save = [('name', None), ('description', None), ('objectID', None), 
                                ('objectType', None),]
        for content_unlocking_rule in content_unlocking_rules:
            # Get basic badge information
            content_unlocking_rule_details = create_item_node(content_unlocking_rule, content_unlocking_rule_fields_to_save)

            rule = content_unlocking_rule.ruleID
            rule_fields_to_save = [('actionID', None), ('awardFrequency', None),]
            # Get the rule information
            rule_details = create_item_node(rule, rule_fields_to_save)

            # Setup Object specifier
            rule_details['objectSpecifier'] = json.loads(rule.objectSpecifier)
            # Get the rule condition string
            rule_condition = content_unlocking_rule.ruleID.conditionID
            rule_details['condition'] = json.loads(databaseConditionToJSONString(rule_condition))

            if post_request:
                validate_content_unlocking_rule_json(content_unlocking_rule_details, post_request, root_json=root_json, messages=messages)

            content_unlocking_rule_details['rule'] = rule_details         

            content_unlocking_rules_jsons.append(content_unlocking_rule_details)
   
    return content_unlocking_rules_jsons

def streaks_to_json(streaks, current_course, post_request=None, root_json=None, messages=[]):
    ''' Converts streaks (AttendanceStreakConfiguration) queryset to json '''

    streaks_jsons = []

    if streaks.exists():
        streaks_fields_to_save = [('daysofClass', None), ('daysDeselected', None),]
        for streak in streaks:
            # Get the streak information
            streak_details = create_item_node(streak, streaks_fields_to_save)

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
            with open(uploaded_file.uploadedFile.name, 'r') as import_stream:
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
                    import_challenge_questions_from_json(root_json['unassigned-problems'], unassigned_challenge, current_course, id_map=id_map, messages=messages)
                
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

    return id_map

#############################################################
# IMPORTING JSON METHODS
#############################################################

def import_topics_from_json(topics_jsons, current_course, context_dict=None, id_map=None, messages=[]):
    ''' Converts topic jsons to model '''

    if topics_jsons:
        for topic_json in topics_jsons:

            # Create a new topic
            # topic_fields_to_save = [('topicName', topic_json['topicName'], None),]
            # topic = create_model_instance(Topics, topic_fields_to_save)       
            topic = create_model_instance(Topics, topic_json)           
            topic.save()


            course_topics = CoursesTopics.objects.filter(topicID__topicName=topic.topicName, courseID=current_course)
            # The imported topic is the same for this course
            if course_topics:  
                course_topic = course_topics.first()                    
            else:
                # Create a new course topic
                # course_topic_fields_to_save = [('topicID', topic, None), ('courseID', current_course, None),]
                course_topic_fields_to_save = {'topicID': topic, 'courseID': current_course}
                # course_topic = create_model_instance(CoursesTopics, course_topic_fields_to_save)
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
                # activity_category_fields_to_save = [('name', activities_categories_json['name'], None),
                #                                     ('courseID', current_course, None),]
                activity_category_fields_to_save = {'courseID': current_course}
                # activity_category = create_model_instance(ActivitiesCategory, activity_category_fields_to_save)
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
            # skill_fields_to_save = [('skillName', skill_json['skillName'], None),]
            # skill = create_model_instance(Skills, skill_fields_to_save) 
            skill = create_model_instance(Skills, skill_json)                 
            skill.save()


            course_skills = CoursesSkills.objects.filter(skillID__skillName=skill.skillName, courseID=current_course)
            # The imported skill is the same for this course
            if course_skills:  
                course_skill = course_skills.first()     
            else:
                # Create a new course skill
                # course_skill_fields_to_save = [('skillID', skill, None), ('courseID', current_course, None),]
                course_skill_fields_to_save = {'skillID': skill, 'courseID': current_course}
                # course_skill = create_model_instance(CoursesSkills, course_skill_fields_to_save)
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
            activity_fields_to_save = [('activityName', activity_json['activityName'], None),
                                        ('isGraded', activity_json['isGraded'], None),
                                        ('description', activity_json['description'], None),
                                        ('points', activity_json['points'], Decimal),
                                        ('isFileAllowed', activity_json['isFileAllowed'], None),
                                        ('uploadAttempts', activity_json['uploadAttempts'], None),
                                        ('instructorNotes', activity_json['instructorNotes'], None),
                                        ('author', activity_json['author'], None),
                                        ('courseID', current_course, None),]

            activity = create_model_instance(Activities, activity_fields_to_save)
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
            challenge_fields_to_save = [('challengeName', challenge_json['challengeName'], None),
                                        ('isGraded', challenge_json['isGraded'], None),
                                        ('numberAttempts', challenge_json['numberAttempts'], None),
                                        ('timeLimit', challenge_json['timeLimit'], None),
                                        ('displayCorrectAnswer', challenge_json['displayCorrectAnswer'], None),
                                        ('displayCorrectAnswerFeedback', challenge_json['displayCorrectAnswerFeedback'], None),
                                        ('displayIncorrectAnswerFeedback', challenge_json['displayIncorrectAnswerFeedback'], None),
                                        ('challengeAuthor', challenge_json['challengeAuthor'], None),
                                        ('challengeDifficulty', challenge_json['challengeDifficulty'], None),
                                        ('challengePassword', challenge_json['challengePassword'], None),
                                        ('startTimestamp', course_config_params.courseStartDate, None),
                                        ('endTimestamp', course_config_params.courseEndDate, None),
                                        ('dueDate', course_config_params.courseEndDate, None),
                                        ('courseID', current_course, None),]

            challenge = create_model_instance(Challenges, challenge_fields_to_save)
            challenge.save()

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

                        challenge_topic_fields_to_save = [('topicID', topic, None), ('challengeID', challenge, None),]        
                        challenge_topic = create_model_instance(ChallengesTopics, challenge_topic_fields_to_save)
                        challenge_topic.save()                
                else:
                    messages.append({'type': 'error', 'message': 'Unable to add topics to challenges. id map not providied'})
            else:
                # Assigned this challenge the default unspecified topic
                course_topic = CoursesTopics.objects.get(courseID=current_course, topicID__topicName=unspecified_topic_name)
                
                if not course_topic:
                    messages.append({'type': 'error', 'message': 'Your Course does not have a unspecified topic. Challenges will not include this topic'})
                    return

                challenge_topic_fields_to_save = [('topicID', course_topic.topicID, None), ('challengeID', challenge, None),]        
                challenge_topic = create_model_instance(ChallengesTopics, challenge_topic_fields_to_save)
                challenge_topic.save()

def import_challenge_questions_from_json(challenge_question_jsons, challenge, current_course, context_dict=None, id_map=None, messages=[]):
    ''' Converts challenge question jsons to model '''

    if challenge_question_jsons:
        for challenge_question_json in challenge_question_jsons:
            # Create the challenge question model instance
            challenge_question_fields_to_save = [('points', challenge_question_json['points'], Decimal),]

            challenge_question = create_model_instance(ChallengesQuestions, challenge_question_fields_to_save)
            
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
            question_fields_to_save = [('preview', question_json['preview'], None), 
                                        ('instructorNotes', question_json['instructorNotes'], None), 
                                        ('type', question_json['type'], None),
                                        ('difficulty', question_json['difficulty'], None), 
                                        ('author', question_json['author'], None),]

            question = create_model_instance(question_type_model, question_fields_to_save)

            if question_type == QuestionTypes.dynamic or question_type == QuestionTypes.templatedynamic:
                dynamic_question_json = question_json['dynamic-question']

                dynamic_question_fields_to_modify = [('numParts', dynamic_question_json['numParts'], None), 
                                                    ('code', dynamic_question_json['code'], None),]

                # Modify the question to add the dynamic question fields
                question = create_model_instance(question, dynamic_question_fields_to_modify, modify=True)

                if question_type == QuestionTypes.templatedynamic:

                    if 'template-dynamic-question' in dynamic_question_json:
                        template_dynamic_question_json = dynamic_question_json['template-dynamic-question']

                        template_dynamic_question_fields_to_modify = [('templateText', template_dynamic_question_json['templateText'], None), 
                                                                    ('setupCode', template_dynamic_question_json['setupCode'], None),]

                        # Modify the question to add the template dynamic question fields
                        question = create_model_instance(question, template_dynamic_question_fields_to_modify, modify=True)
                        question.save()

                        # Create the template text parts
                        if 'template-text-parts' in template_dynamic_question_json:

                            for template_text_part_json in template_dynamic_question_json['template-text-parts']:
                                template_text_part_fields_to_save = [('partNumber', template_text_part_json['partNumber'], None), 
                                                                    ('templateText', template_text_part_json['templateText'], None),
                                                                    ('dynamicQuestion', question, None),]

                                template_text_part = create_model_instance(TemplateTextParts, template_text_part_fields_to_save)
                                template_text_part.save()
                        else:
                            messages.append({'type': 'error', 'message': 'Template Dynamic Question does not have any template text parts'})

                    else:
                        messages.append({'type': 'error', 'message': 'Tempalte Dynamic Question is not valid'})

                else:
                    question.save()

                # Create QuestionLibraries if any
                if 'question-libraries' in dynamic_question_json:

                    for question_library_json in dynamic_question_json['question-libraries']:
                        # Get the lua library and link it to the question
                        lua_library = LuaLibrary.objects.get(libarayName=question_library_json['libraryName'])
                        question_library_fields_to_save = [('question', question, None), ('library', lua_library, None),]

                        question_library = create_model_instance(QuestionLibrary, question_library_fields_to_save)
                        question_library.save() 
            else:
                # Question type is static questions
                static_question_json = question_json['static-question']

                static_question_fields_to_modify = [('questionText', static_question_json['questionText'], None), 
                                                ('correctAnswerFeedback', static_question_json['correctAnswerFeedback'], None), 
                                                ('incorrectAnswerFeedback', static_question_json['incorrectAnswerFeedback'], None),]

                question = create_model_instance(question, static_question_fields_to_modify, modify=True)
                question.save()

                if 'answers' in static_question_json:

                    for answer_json in static_question_json['answers']:
                        static_question_answers_fields_to_save = [('answerText', answer_json['answerText'], None),
                                                                ('questionID', question, None),]

                        static_question_answer = create_model_instance(Answers, static_question_answers_fields_to_save)
                        static_question_answer.save()

                        # Create the correct answer if this is the correct answer of the question
                        if 'correctAnswer' in answer_json:
                            correct_answers_fields_to_save = [('answerID', static_question_answer, None),
                                                                ('questionID', question, None),]

                            correct_answer = create_model_instance(CorrectAnswers, correct_answers_fields_to_save)
                            correct_answer.save()
                        
                        # Create matching answers if any
                        if 'matchingAnswerText' in answer_json:
                            matching_answers_fields_to_save = [('answerID', static_question_answer, None),
                                                                ('questionID', question, None),
                                                                ('matchingAnswerText', answer_json['matchingAnswerText'], None),]

                            matching_answer = create_model_instance(MatchingAnswers, matching_answers_fields_to_save)
                            matching_answer.save()
                else:
                    messages.append({'type': 'error', 'message': 'Static Question does not have any answers'})

            # Create question skills if any
            if 'skills' in challenge_question_json['question']:
                if id_map:
                    for question_skill_json in challenge_question_json['question']['skills']:                        
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

                        question_skill_fields_to_save = [('skillID', skill, None), ('questionID', question, None),
                                                        ('questionSkillPoints', question_skill_json['questionSkillPoints'], None),
                                                        ('courseID', current_course, None),]        
                        question_skill = create_model_instance(QuestionsSkills, question_skill_fields_to_save)
                        question_skill.save()                
                else:
                    messages.append({'type': 'error', 'message': 'Unable to add skills to challenge questions. id map not providied'})

            # Save the challenge question
            challenge_question_fields_to_modify = [('challengeID', challenge, None),
                                                ('questionID', question, None),]
            challenge_question = create_model_instance(challenge_question, challenge_question_fields_to_modify, modify=True)
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
            condition_fields_to_save = [('courseID', current_course, None),
                                        ('operation', condition_json['op'], None),
                                        ('operand1Type', OperandTypes.systemVariable, None),
                                        ('operand1Value', condition_json['lhs'], int),]

            condition = create_model_instance(Conditions, condition_fields_to_save)

            operand_2_type = condition_json['rhstype']
            
            value_to_save = condition_json['rhsvalue']

            if operand_2_type == "V" or operand_2_type == "N" or operand_2_type == "X":
                # System Variable or Immeditate Integer or Boolean
                operand_2_value = value_to_save
            elif operand_2_type == "T":
                # String Constant
                string_constant = create_model_instance(StringConstants, [('stringValue', value_to_save, None),])
                string_constant.save()
                operand_2_value = string_constant.stringID
            elif operand_2_type == "Y":
                # Date Constant
                date_constant = create_model_instance(Dates, [('dateValue', utcDate(value_to_save, '%Y-%M-%d').date(), None),])
                date_constant.save()
                operand_2_value = date_constant.dateID
            
            condition_fields_to_update = [('operand2Type', char_operand_types_map[operand_2_type], None),
                                        ('operand2Value', operand_2_value, int),]
            # Modify condition to add the two fields
            # Note operand_2_value will be converted to int before saving
            condition = create_model_instance(condition, condition_fields_to_update, modify=True)
            condition.save()

            return condition
        elif condition_json['type'] == 'AND' or condition_json['type'] == 'OR':
            # Create the condition to hold the children conditions
            condition_fields_to_save = [('courseID', current_course, None),
                                        ('operation', condition_json['type'], None),
                                        ('operand1Type', OperandTypes.conditionSet, None),
                                        ('operand1Value', 0, None),
                                        ('operand2Type', OperandTypes.noOperand, None),
                                        ('operand2Value', 0, None),]

            condition = create_model_instance(Conditions, condition_fields_to_save)
            condition.save()
            
            # Set up condition set relationships between this condition and sub condition
            for sub_condition_json in condition_json['subConds']:
                # Create sub condition from json
                sub_condition = import_condition_from_json(sub_condition_json, current_course, id_map=id_map)
                if sub_condition:
                    condition_set_fields_to_save = [('parentCondition', condition, None), ('conditionInSet', sub_condition, None),]
                    condition_set = create_model_instance(ConditionSet, condition_set_fields_to_save)
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

            condition_fields_to_save = [('courseID', current_course, None),
                                        ('operation', operation, None),
                                        ('operand1Type', operand_1_type, None),
                                        ('operand1Value', not condition_json['allObjects'], int), # This has a not since when exported True values actually mean 0 (see conditions_utils.py)
                                        ('operand2Type', operand_2_type, None),
                                        ('operand2Value', operand_2_value, int),]

            condition = create_model_instance(Conditions, condition_fields_to_save)
            condition.save()

            if 'objects' in condition_json and condition_json['objects']:

                if condition.operand1Type == OperandTypes.activitySet:
                    # Create the activity set for each object id
                    for activity_id in condition_json['objects']:
                        mapped_activity_id = search_for_mapped_id('activities', int(activity_id), id_map=id_map)
                        if not mapped_activity_id:
                            messages.append({'type': 'error', 'message': 'Unable to find activity id in mapped ids dictionary for conditions'})
                            continue

                        activity_set_fields_to_save = [('activity_id', mapped_activity_id, int), ('condition', condition, None),]
                        activity_set = create_model_instance(ActivitySet, activity_set_fields_to_save)
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

                        challenge_set_fields_to_save = [('challenge_id', mapped_challenge_id, int), ('condition', condition, None),]
                        challenge_set = create_model_instance(ChallengeSet, challenge_set_fields_to_save)
                        challenge_set.save()
                        
                elif condition.operand1Type == OperandTypes.topicSet:
                    # Create the topic set for each object id
                    for topic_id in condition_json['objects']:
                        mapped_topic_id = search_for_mapped_id('topics', int(topic_id), id_map=id_map)
                        if not mapped_topic_id:
                            messages.append({'type': 'error', 'message': 'Unable to find topic id in mapped ids dictionary for conditions'})
                            continue

                        topic_set_fields_to_save = [('topic_id', mapped_topic_id, int), ('condition', condition, None),]
                        topic_set = create_model_instance(TopicSet, topic_set_fields_to_save)
                        topic_set.save()

                elif condition.operand1Type == OperandTypes.activtiyCategorySet:
                    # Create the activity category set for each object id
                    for activity_category_id in condition_json['objects']:
                        mapped_activity_category_id = search_for_mapped_id('activities-categories', int(activity_category_id), id_map=id_map)
                        if not mapped_activity_category_id:
                            messages.append({'type': 'error', 'message': 'Unable to find activity category id in mapped ids dictionary for conditions'})
                            continue

                        activity_category_set_fields_to_save = [('category_id', mapped_activity_category_id, int), ('condition', condition, None),]
                        activity_category_set = create_model_instance(ActivityCategorySet, activity_category_set_fields_to_save)
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

        rule_fields_to_save = [('courseID', current_course, None), ('conditionID', condition, None), ('actionID', rule_json['actionID'], None),
                                ('objectSpecifier', object_specifier, None), ('awardFrequency', rule_json['awardFrequency'], None),]

        rule = create_model_instance(Rules, rule_fields_to_save)
        rule.save()

        # Create rule events
        events = get_events_for_condition(condition, object_type)
        for event, isGlobal in events:
            rule_event_fields_to_save = [('rule', rule, None), ('event', event, None), ('inGlobalContext', isGlobal, None),]
            rule_event = create_model_instance(RuleEvents, rule_event_fields_to_save)
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

            badge_fields_to_save = [('badgeName', badge_json['badgeName'], None), 
                                                ('badgeDescription', badge_json['badgeDescription'], None), 
                                                ('badgeImage', badge_json['badgeImage'], None), 
                                                ('manual', badge_json['manual'], None), 
                                                ('isPeriodic', badge_json['isPeriodic'], None),
                                                ('courseID', current_course, None),]

            badge = create_model_instance(badge_type_model, badge_fields_to_save)

            if badge_type == 'automatic':
                rule_json = badge_json['rule']

                # Create the rule
                rule = import_rule_json(rule_json, current_course, id_map=id_map, messages=messages)

                # Failed to create rule so don't create the badge (error is shown in import_rule_json)
                if rule is None:
                    continue

                # Set the badge rule
                badge = create_model_instance(badge, [('ruleID', rule, None)], modify=True)
                badge.save()

                # Create action argument for badge
                action_argument_fields_to_save = [('ruleID', rule, None), ('sequenceNumber', 1, None), ('argumentValue', badge.badgeID, str),]
                
                action_argument = create_model_instance(ActionArguments, action_argument_fields_to_save)
                action_argument.save() 

            elif badge_type == 'periodic':
                # Add the periodic fields to badge
                periodic_badge_fields_to_update = [('periodicVariableID', badge_json['periodicVariableID'], None), ('timePeriodID', badge_json['timePeriodID'], None),
                                                ('periodicType', badge_json['periodicType'], None), ('numberOfAwards', badge_json['numberOfAwards'], None), 
                                                ('threshold', badge_json['threshold'], None), ('operatorType', badge_json['operatorType'], None),
                                                ('isRandom', badge_json['isRandom'], None), ('resetStreak', badge_json['resetStreak'], None),
                                                ('lastModified', utcDate(), None),]
                
                badge = create_model_instance(badge, periodic_badge_fields_to_update, modify=True)
                badge.save()
                
                # Create the periodic task 
                if badge_json['periodicType'] == 0:
                    # TopN
                    badge = create_model_instance(badge, [('periodicTask', setup_periodic_badge(unique_id=int(badge.badgeID), badge_id=int(badge.badgeID), variable_index=int(badge.periodicVariableID), course=current_course, period_index=int(badge.timePeriodID), number_of_top_students=int(badge.numberOfAwards), threshold=int(badge.threshold), operator_type=badge.operatorType), None),], modify=True)
                elif badge_json['periodicType'] == 2:
                    # Random
                    badge = create_model_instance(badge, [('periodicTask', setup_periodic_badge(unique_id=int(badge.badgeID), badge_id=int(badge.badgeID), variable_index=int(badge.periodicVariableID), course=current_course, period_index=int(badge.timePeriodID), threshold=int(badge.threshold), operator_type=badge.operatorType, is_random=badge.isRandom), None),], modify=True)
                else:
                    # All (1)
                    badge = create_model_instance(badge, [('periodicTask', setup_periodic_badge(unique_id=int(badge.badgeID), badge_id=int(badge.badgeID), variable_index=int(badge.periodicVariableID), course=current_course, period_index=int(badge.timePeriodID), threshold=int(badge.threshold), operator_type=badge.operatorType), None),], modify=True)
                
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

            vc_rule_fields_to_save = [('vcRuleName', vc_rule_json['vcRuleName'], None), ('vcRuleDescription', vc_rule_json['vcRuleDescription'], None), 
                                    ('vcRuleType', vc_rule_json['vcRuleType'], None), ('vcRuleAmount', vc_rule_json['vcRuleAmount'], None), 
                                    ('vcRuleLimit', vc_rule_json['vcRuleLimit'], None), ('isPeriodic', vc_rule_json['isPeriodic'], None),
                                    ('courseID', current_course, None),]

            vc_rule = create_model_instance(vc_rule_type_model, vc_rule_fields_to_save)

            if vc_rule_type == 'automatic':
                rule_json = vc_rule_json['rule']

                # Create the rule
                rule = import_rule_json(rule_json, current_course, id_map=id_map, messages=messages)

                # Failed to create rule so don't create the vc rule (error is shown in import_rule_json)
                if rule is None:
                    continue

                # Set the vc rule to include new rule
                vc_rule = create_model_instance(vc_rule, [('ruleID', rule, None)], modify=True)
                vc_rule.save()

                # Create action argument for vc rule
                # NOTE: Argument value is set to same as when saving virtual currency earning rule (see saveVirtualCurrencyRule.py)
                # if this value is changed, it needs to be updated here as well
                action_argument_fields_to_save = [('ruleID', rule, None), ('sequenceNumber', 1, None), ('argumentValue', 0, str),]
                
                action_argument = create_model_instance(ActionArguments, action_argument_fields_to_save)
                action_argument.save() 

            elif vc_rule_type == 'periodic':
                # Add the periodic fields to vc rule
                periodic_vc_rule_fields_to_update = [('periodicVariableID', vc_rule_json['periodicVariableID'], None), ('timePeriodID', vc_rule_json['timePeriodID'], None),
                                                ('periodicType', vc_rule_json['periodicType'], None), ('numberOfAwards', vc_rule_json['numberOfAwards'], None), 
                                                ('threshold', vc_rule_json['threshold'], None), ('operatorType', vc_rule_json['operatorType'], None),
                                                ('isRandom', vc_rule_json['isRandom'], None), ('resetStreak', vc_rule_json['resetStreak'], None),
                                                ('lastModified', utcDate(), None),]
                
                vc_rule = create_model_instance(vc_rule, periodic_vc_rule_fields_to_update, modify=True)
                vc_rule.save()
                
                # Create the periodic task 
                if vc_rule_json['periodicType'] == 0:
                    # TopN
                    vc_rule = create_model_instance(vc_rule, [('periodicTask', setup_periodic_vc(unique_id=int(vc_rule.vcRuleID), virtual_currency_amount=int(vc_rule.vcRuleAmount), variable_index=int(vc_rule.periodicVariableID), course=current_course, period_index=int(vc_rule.timePeriodID), number_of_top_students=int(vc_rule.numberOfAwards), threshold=int(vc_rule.threshold), operator_type=vc_rule.operatorType), None),], modify=True)
                elif vc_rule_json['periodicType'] == 2:
                    # Random
                    vc_rule = create_model_instance(vc_rule, [('periodicTask', setup_periodic_vc(unique_id=int(vc_rule.vcRuleID), virtual_currency_amount=int(vc_rule.vcRuleAmount), variable_index=int(vc_rule.periodicVariableID), course=current_course, period_index=int(vc_rule.timePeriodID), threshold=int(vc_rule.threshold), operator_type=vc_rule.operatorType, is_random=vc_rule.isRandom), None),], modify=True)
                else:
                    # All (1)
                    vc_rule = create_model_instance(vc_rule, [('periodicTask', setup_periodic_vc(unique_id=int(vc_rule.vcRuleID), virtual_currency_amount=int(vc_rule.vcRuleAmount), variable_index=int(vc_rule.periodicVariableID), course=current_course, period_index=int(vc_rule.timePeriodID), threshold=int(vc_rule.threshold), operator_type=vc_rule.operatorType), None),], modify=True)
                
                vc_rule.save()
            elif vc_rule_type == 'spending':
                # Create the default spending condition
                condition_fields_to_save = [('operation', '=', None), ('operand1Type', OperandTypes.immediateInteger, None),
                                            ('operand1Value', 1, None), ('operand2Type', OperandTypes.immediateInteger, None),
                                            ('operand2Value', 1, None), ('courseID', current_course, None),]

                condition = create_model_instance(Conditions, condition_fields_to_save)
                condition.save()

                rule_fields_to_save = [('courseID', current_course, None), ('conditionID', condition, None), 
                                        ('actionID', Action.decreaseVirtualCurrency, None),]

                rule = create_model_instance(Rules, rule_fields_to_save)
                rule.save()

                # Create rule event
                rule_event_fields_to_save = [('rule', rule, None), ('event', Event.spendingVirtualCurrency, None),]
                rule_event = create_model_instance(RuleEvents, rule_event_fields_to_save)
                rule_event.save()

                # Set the vc rule to include new rule
                vc_rule = create_model_instance(vc_rule, [('ruleID', rule, None)], modify=True)
                vc_rule.save()

                # Create action argument for vc rule
                action_argument_fields_to_save = [('ruleID', rule, None), ('sequenceNumber', 1, None), ('argumentValue', vc_rule_json['vcRuleAmount'], str),]
                
                action_argument = create_model_instance(ActionArguments, action_argument_fields_to_save)
                action_argument.save()

            else:
                # vc rule is manual
                vc_rule.save()

def import_leaderboards_from_json(leaderboards_jsons, current_course, id_map=None, messages=[]):
    ''' Converts a leaderboard to model '''

    if leaderboards_jsons:
        for leaderboard_json in leaderboards_jsons:

            # Create the leaderboard model instance
            leaderboard_fields_to_save = [('leaderboardName', leaderboard_json['leaderboardName'], None), 
                                        ('leaderboardDescription', leaderboard_json['leaderboardDescription'], None),
                                        ('isContinous', leaderboard_json['isContinous'], None),
                                        ('isXpLeaderboard', leaderboard_json['isXpLeaderboard'], None), 
                                        ('numStudentsDisplayed', leaderboard_json['numStudentsDisplayed'], None),
                                        ('periodicVariable', leaderboard_json['periodicVariable'], None), 
                                        ('timePeriodUpdateInterval', leaderboard_json['timePeriodUpdateInterval'], None), 
                                        ('displayOnCourseHomePage', leaderboard_json['displayOnCourseHomePage'], None), 
                                        ('howFarBack', leaderboard_json['howFarBack'], None),
                                        ('lastModified', utcDate(), None),
                                        ('courseID', current_course, None),]

            leaderboard = create_model_instance(LeaderboardsConfig, leaderboard_fields_to_save)
            leaderboard.save()

            # Create periodic task for leaderboard
            leaderboard = create_model_instance(leaderboard, [('periodicTask', setup_periodic_leaderboard(leaderboard_id=leaderboard.leaderboardID, variable_index=leaderboard.periodicVariable, course=leaderboard.courseID, period_index=leaderboard.timePeriodUpdateInterval,  number_of_top_students=leaderboard.numStudentsDisplayed, threshold=1, operator_type='>', is_random=None), None),], modify=True)
            leaderboard.save()

def import_content_unlocking_rules_from_json(content_unlocking_rules_jsons, current_course, id_map=None, messages=[]):
    ''' Converts a content unlocking rule to model '''

    if content_unlocking_rules_jsons:
        for content_unlocking_rule_json in content_unlocking_rules_jsons:

            # Create the badge model instance for type
            content_unlocking_rule_fields_to_save = [('name', content_unlocking_rule_json['name'], None), 
                                                    ('description', content_unlocking_rule_json['description'], None), 
                                                    ('objectID', content_unlocking_rule_json['objectID'], None), 
                                                    ('objectType', content_unlocking_rule_json['objectType'], None),
                                                    ('courseID', current_course, None),]

            content_unlocking_rule = create_model_instance(ProgressiveUnlocking, content_unlocking_rule_fields_to_save)

            rule_json = content_unlocking_rule_json['rule']

            # Create the rule
            rule = import_rule_json(rule_json, current_course, id_map=id_map, messages=messages)

            # Failed to create rule so don't create the content unlocking rule (error is shown in import_rule_json)
            if rule is None:
                continue

            # Set the content unlocking rule to include new rule
            content_unlocking_rule = create_model_instance(content_unlocking_rule, [('ruleID', rule, None)], modify=True)
            content_unlocking_rule.save()

            # Create action argument for content unlocking rule
            action_argument_fields_to_save = [('ruleID', rule, None), ('sequenceNumber', 1, None), ('argumentValue', content_unlocking_rule.pk, str),]
            
            action_argument = create_model_instance(ActionArguments, action_argument_fields_to_save)
            action_argument.save() 

            # Make Student objects for the content unlocking rule
            students_registered_courses = StudentRegisteredCourses.objects.filter(courseID=current_course)
            for students_registered_course in students_registered_courses:
                
                student_content_unlocking_fields_to_save = [('studentID', students_registered_course.studentID, None), ('pUnlockingRuleID', content_unlocking_rule, None), 
                                                            ('courseID', current_course, None), ('objectID', content_unlocking_rule_json['objectID'], None),
                                                            ('objectType', content_unlocking_rule_json['objectType'], None),]

                student_content_unlocking =  create_model_instance(StudentProgressiveUnlocking, student_content_unlocking_fields_to_save)
                student_content_unlocking.save()

def import_streaks_from_json(streaks_jsons, current_course, id_map=None, messages=[]):
    ''' Converts a streak (AttendanceStreakConfiguration) to model '''

    if streaks_jsons:
        for streak_json in streaks_jsons:
            
            # Create the streak model instance
            streaks_fields_to_save = [('daysofClass', streak_json['daysofClass'], None), 
                                    ('daysDeselected', streak_json['daysDeselected'], None),
                                    ('courseID', current_course, None),]
            
            streak = create_model_instance(AttendanceStreakConfiguration, streaks_fields_to_save)
            streak.save()