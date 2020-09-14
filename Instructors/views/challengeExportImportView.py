'''
Created on May 1, 2017

@author: dichevad
'''
from django.shortcuts import redirect, render, HttpResponse

from Instructors.models import Courses, Challenges, CoursesSkills, CoursesTopics, ChallengesTopics, ChallengesQuestions, StaticQuestions 
from Instructors.models import UploadedFiles 
from Instructors.models import QuestionsSkills, Skills
from Instructors.constants import unspecified_topic_name, unassigned_problems_challenge_name
from Instructors.views.utils import initialContextDict
from Instructors.views.courseImportExportView import ensure_directory, topics_to_json, challenges_to_json, course_skills_to_json, import_topics_from_json, import_challenges_from_json, import_course_skills_from_json
from decimal import Decimal
from django.http import JsonResponse
from Badges.models import CourseConfigParams
from Instructors.constants import unassigned_problems_challenge_name
import json
import os
import zipfile
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from oneUp.settings import MEDIA_ROOT
from oneUp.decorators import instructorsCheck  

LUA_PROBLEMS_ROOT = os.path.join(settings.BASE_DIR, 'lua/problems/')
VERSION = "1.0"

def str2bool(value):
    return value in ('True', 'true') 

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')  
def exportChallenge(request):
    context_dict, current_course = initialContextDict(request)
    context_dict['version'] = VERSION
    if request.method == 'GET':
        chall_name = [] 
        chall_ID = []      
        challenges = Challenges.objects.filter(courseID=current_course)        
        for challenge in challenges:
            chall_name.append(challenge.challengeName)
            chall_ID.append(challenge.challengeID)
        
        zipped = zip(range(1, len(chall_name) + 1), chall_ID, chall_name)
        ##GGM sort the item alphabetically
        context_dict['challenge_range'] = sorted(zipped, key=lambda x: x[2])
        return render(request,'Instructors/ChallengeExport.html', context_dict)

    if request.method == 'POST':
       
        
        root_json = json.loads(request.POST.get('exported-json', ''))
        # Only export json if the json contains items other than the version number
        if 'version' in root_json and len(root_json) > 1:
            file_name = 'media/textfiles/challenges/json/challenges-{}-{}.zip'.format(current_course.courseName, VERSION)
            ensure_directory('media/textfiles/challenges/json/')
            try:
                os.remove(file_name)
            except:
                print("File doesn't exist ", file_name)
            with zipfile.ZipFile(file_name, 'a') as zip_file:
                # Add the json for challenges
                zip_file.writestr('challenges.json', json.dumps(root_json).encode('utf-8'))
                
                # Add the folders to the zip file
                if 'code-paths' in root_json:
                    for path in root_json['code-paths']:
                        zip_directory(os.path.join(LUA_PROBLEMS_ROOT, path), zip_file)

                # print(zip_file.printdir())

            response = HttpResponse(open(file_name, 'rb'), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename=challenges-{}-{}.zip'.format(current_course.courseName, VERSION)

            return response
        return render(request,'Instructors/ChallengeExport.html', context_dict)
    

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')         
def validateChallengeExport(request):
    context_dict, current_course = initialContextDict(request)
    if request.method == 'POST':
        messages = []
        response = {}
        root_json = {}
        
        # Notify user about field export decisions
        messages.append({'type': 'info', 'message': 'Challenges Display From, Display To, and Due Date will not be exported. These options should be set after importing'})


        # get the list of all checked challenges
        selected = request.POST.getlist('selected')
        
        challenges = []
        if selected:
            selected_ids = [int(x) for x in selected]
            challenges = Challenges.objects.filter(pk__in=selected_ids)
        else:
            challenges = Challenges.objects.filter(courseID=current_course) 

        # Create the json based on which checkbox is selected
        topic_ids = set()
        skill_ids = set()
        for challenge in challenges:
            challenge_topic = ChallengesTopics.objects.filter(challengeID=challenge)
            challenge_questions = ChallengesQuestions.objects.filter(challengeID=challenge)
            if challenge_topic:
                topic_ids.add(challenge_topic.first().topicID)
               
            for question in challenge_questions:
                skill = QuestionsSkills.objects.filter(questionID=question.questionID, courseID=current_course).first()
                if skill:
                    skill_ids.add(skill.skillID)
        topics = CoursesTopics.objects.filter(courseID=current_course, topicID__in=list(topic_ids))
        root_json['topics'] = topics_to_json(topics, current_course, messages=messages)

        
        course_skills = CoursesSkills.objects.filter(courseID=current_course, skillID__in=list(skill_ids))
        root_json['skills'] = course_skills_to_json(course_skills, current_course, messages=messages)


        # Exclude unassigned challenge since that is created by default for every course
        serious_challenges = challenges.filter(courseID=current_course, isGraded=True).exclude(challengeName=unassigned_problems_challenge_name)
        root_json['serious-challenges'] = challenges_to_json(serious_challenges, current_course, include_topics=True, root_json=root_json, messages=messages)

        # Exclude unassigned challenge since that is created by default for every course
        warmup_challenges = challenges.filter(courseID=current_course, isGraded=False).exclude(challengeName=unassigned_problems_challenge_name)
        root_json['warmup-challenges'] = challenges_to_json(warmup_challenges, current_course, include_topics=True, root_json=root_json, messages=messages)
        
        # Versioning
        root_json['version'] = VERSION
    # Get rid of duplicate messages by converting list of dicts 
        # to set of tuples then back to list of dicts
        messages = [dict(t) for t in {tuple(d.items()) for d in messages}]
        response['messages'] = messages
        
        response['exported-json'] = root_json
        # Debug messages
        ensure_directory('media/textfiles/challenges/json/')
        with open('media/textfiles/challenges/json/export-log.json', 'w') as export_stream:
                json.dump(root_json, export_stream)

        return JsonResponse(response)
    
    return JsonResponse({'messages': [{'type': 'error', 'message': 'Error in validation export challenges request'}]})

@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')     
def importChallenge(request):
    context_dict, current_course = initialContextDict(request)
       
    if request.method == 'GET':
        return render(request,'Instructors/ChallengeImport.html', context_dict)
    
    if request.method == 'POST':
        if 'challenges' in request.FILES:
            response = {}

            # Holds the messages to display for the user in the frontend
            messages = []

            challenge_json = request.FILES['challenges']
            root_json = {}
            
            uploaded_file = UploadedFiles() 
            uploaded_file.uploadedFile = challenge_json     
            uploaded_file.uploadedFileName = challenge_json.name
            uploaded_file.uploadedFileCreator = request.user
            uploaded_file.save()

            # It is important we use uploaded_file.uploadedFile.name because
            # if there are two files with the same name, the file will
            # get renamed. This includes the rename
            with zipfile.ZipFile(uploaded_file.uploadedFile.name) as zip_file:
                with zip_file.open('challenges.json') as import_stream:
                    root_json = json.load(import_stream)

                if root_json:

                    id_map = {}
                    if 'topics' in root_json:
                        id_map['topics'] = {}
                
                    if 'skills' in root_json:
                        id_map['skills'] = {}
                
                    if 'serious-challenges' in root_json:
                        id_map['serious-challenges'] = {}
                    if 'warmup-challenges' in root_json:
                        id_map['warmup-challenges'] = {}
                    if 'code-paths' in root_json:
                        id_map['code-paths'] = {}
                    # Notify user about field export decisions
                    messages.append({'type': 'info', 'message': 'Challenges Display From, Display To, and Due Date was set to Course Start Date, Course End Date, and Course End Date respectively'})
                    if 'topics' in root_json:
                        import_topics_from_json(root_json['topics'], current_course, id_map=id_map, messages=messages)
                    
                    if 'skills' in root_json:
                        import_course_skills_from_json(root_json['skills'], current_course, id_map=id_map, messages=messages)
                    if 'serious-challenges' in root_json:
                        import_challenges_from_json(root_json['serious-challenges'], current_course, context_dict=context_dict, id_map=id_map, messages=messages)
                    
                    if 'warmup-challenges' in root_json:
                        import_challenges_from_json(root_json['warmup-challenges'], current_course, context_dict=context_dict, id_map=id_map, messages=messages)
                    
                else:
                    messages.append({'type': 'error', 'message': 'File: {} is empty or cannot be read'.format(uploaded_file.uploadedFile.name)})



            uploaded_file.delete()  

            # Get rid of duplicate messages by converting list of dicts 
            # to set of tuples then back to list of dicts
            messages = [dict(t) for t in {tuple(d.items()) for d in messages}]
            response['messages'] = messages
            
            # Debug messages
            ensure_directory('media/textfiles/challenges/json/')
            with open('media/textfiles/challenges/json/import-log.json', 'w') as import_stream:
                json.dump(messages, import_stream)

            return JsonResponse(response)
    
    return JsonResponse({'messages': [{'type': 'error', 'message': 'Error in the request for importing a challenge'}]})

