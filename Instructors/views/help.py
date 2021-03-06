#import nltk
from Instructors.models import CoursesTopics, Tags, Skills, ChallengeTags, ResourceTags, QuestionsSkills, Topics, ChallengesTopics, CoursesSkills, Courses
from Instructors.constants import unspecified_topic_name
from Badges.models import CourseConfigParams
from Badges.enums import ObjectTypes
import re
import string
from django.contrib.auth.decorators import login_required
from oneUp.logger import logger
import json
import pytz
from datetime import datetime, timezone

def saveSkills(skillstring, resource, resourceIndicator):
    #if skillstring is not null or empty
    if not skillstring == "":
        
        #split string into an array 
        skillsList = skillstring.split(',') 
                    
        for skillWord in skillsList:
            
            # removing leading and trailing white spaces
            skillWord = skillWord.strip()

            skillExists = False  #used to check if a tag exists already
            
            #create a new tag-object; check what is tagged object - question or challenge               
            if resourceIndicator == "question":
                newSkillsObject = QuestionsSkills()
            
            #if the tag already exists... set tagExists to 1
            for item in Skills.objects.all():
                if skillWord == str(item.skillName):
                    skillExists = True
                    break

            if not skillExists:
                #create new tag                    
                newSkill = Skills()
                newSkill.SkillName = skillWord
                newSkill.save()

            for tempSkill in Skills.objects.all():
                if tempSkill.skillName == skillWord:
                    #check if there is such tag for this resource
                    
                    newSkillsObject.skillID = Skills(tempSkill.skillID)
                    print (str("Tagid: ") + str(tempSkill.skillID))
                    break
            
            if resourceIndicator == "question":
                newSkillsObject.questionID = resource
                print (str("questionID: ") + str(newSkillsObject.questionID))
                print (str(newSkillsObject.questionID))
                newSkillsObject.save()
                                        
def saveTags(tagString, resource, resourceType): 
    tags = json.loads(tagString)
    logger.debug("[POST] tags: " + str(tags))
    newTags = [tag['tag'] for tag in tags]
    if len(tags) > 0:
        for tag in newTags: 
            tagExists = False                           
            for item in Tags.objects.all():
                if tag == str(item.tagName):
                    tagExists = True
                    break
            if not tagExists:
                #create new tag                    
                newTag = Tags()
                newTag.tagName = tag
                newTag.save()
   
    # delete all previous tags for this challenge
    if resourceType == ObjectTypes.challenge:
        resourceTags = ChallengeTags.objects.filter(challengeID = resource.challengeID).delete()
    elif resourceType == ObjectTypes.question:
        resourceTags = ResourceTags.objects.filter(questionID = resource.questionID).delete()
        
    # now add the new tags for this challenge 
    for tag in newTags:                 
        #create a new tag-challenge object    
        if resourceType == ObjectTypes.challenge:          
            newTagsObject = ChallengeTags()
            newTagsObject.challengeID = resource
        elif resourceType == ObjectTypes.question:
            newTagsObject = ResourceTags()
            newTagsObject.questionID = resource
        # find tagID
        for tempTag in Tags.objects.all():
            if tempTag.tagName == tag:
                newTagsObject.tagID = Tags.objects.get(pk=tempTag.tagID)
                break                
        newTagsObject.save()
                                
def saveQuestionSkills(skillstring, question, course):
    #if skillstring is not null or empty
    if not skillstring == "":
        
        # delete all previous skill for this question and course
        resourceSkills = QuestionsSkills.objects.filter(questionID = question.questionID).delete()
            
        #split string into an array 
        skillsList = skillstring.split(',')
        #print(skillsList)
        #Break the elements in skillslist of name and skill points
        for skill in skillsList:
            #skillName, skillPoints = skill.word_tokenize()
            skillName, skillPoints = skill.split('(')
            
            # removing leading and trailing white spaces
            skillName = skillName.strip()
            skillPoints = skillPoints[:-1]
            print ("skillName: "+skillName)
            print ("skillPoints: "+skillPoints)
            
            # find the skillID for this skillName
            for s in Skills.objects.all():
                if skillName == s.skillName:
                    skillID = s.skillID

                            
            # now add the new skill for this question                 
            # Check if skill is created of same type (AH)
            createdSkill = QuestionsSkills.objects.filter(skillID = skillID, questionID = question.questionID, courseID = course)
            
            if (createdSkill):
                # Update skill with the new skillPoints (AH)
                skillObj = createdSkill[0]
                skillObj.questionSkillPoints = int(skillPoints)
                skillObj.save()
            else:              
                # create a new skill-question object
                newQSkillsObject = QuestionsSkills()
                newQSkillsObject.questionID = question
                newQSkillsObject.courseID = course
                newQSkillsObject.questionSkillPoints = int(skillPoints)
                newQSkillsObject.skillID = Skills(skillID)                
                
                newQSkillsObject.save()
    else:
        # delete all previous skill for this question and course                            #AA 3/24/15
        resourceSkills = QuestionsSkills.objects.filter(questionID = question.questionID).delete()                                           

def saveChallengesTopics(topicstring, challenge, unspecified_topic):        
    oldChallTopicNames = []
    oldChallengeTopics = ChallengesTopics.objects.filter(challengeID = challenge.challengeID)
    for ct in oldChallengeTopics:
        oldChallTopicNames.append(ct.topicID.topicName)

    #if topicstring is not null or empty
    if topicstring == "":
        
        newTopicNames = set() 
        if not topicstring == "":              
        #split string into an array 
            topicsList = topicstring.split(',')       
            for topic in topicsList:
                if not topic == '':
                    newTopicNames.add(topic.strip())
        else:
            newTopicNames.add(unspecified_topic_name)           
        print(newTopicNames)

        # Remove old topics for the challenge which are not in the list  of new topics  
        for ct in oldChallengeTopics:
            #if not ct.topicID.topicName in newTopicNames and not ct.topicID.topicName==unspecified_topic_name:
            if not ct.topicID.topicName in newTopicNames:
                ct.delete()
        
        # add the new topics for this challenge
        for topicName in newTopicNames:            

            if not topicName in oldChallTopicNames:                                              
                newCTopicsObject = ChallengesTopics()
                newCTopicsObject.challengeID = challenge
                topic = Topics.objects.filter(topicName=topicName)               
                newCTopicsObject.topicID = Topics.objects.get(pk=topicName)            
                newCTopicsObject.save()
                                    
    else:
        # no new topics specified
        # Remove old topics for the challenge which are not in the list  of new topics              
        if not unspecified_topic_name in oldChallTopicNames:
            for ct in oldChallengeTopics:                    
                ct.delete()
            # Assign Unspecified topic to this challenge
            newChallTopicsObject = ChallengesTopics()
            newChallTopicsObject.challengeID = challenge
            newChallTopicsObject.topicID = unspecified_topic                
            newChallTopicsObject.save()
                                                                                                         
def extractTags(resource, resourceIndicator):   
    if resourceIndicator == "question":
        resourceTags = ResourceTags.objects.filter(questionID = resource.questionID)
    elif resourceIndicator == "challenge":
        resourceTags = ChallengeTags.objects.filter(challengeID = resource.challengeID)

    tags = []
    for t in resourceTags:
        tag = {}
        tag['tag'] = t.tagID.tagName
        tags.append(tag)

    logger.debug("Tags To JSON: " + json.dumps(tags))
    return json.dumps(tags)  

def extractSkills(resource, resourceIndicator):   

    if resourceIndicator == "question":
        resourceSkills = QuestionsSkills.objects.filter(questionID = resource.questionID)
     
    skill_ID = []
    skill_Name = []
    skill_Points = []
    count = 1
    
    # Add skills to the list with id, name, and points that will be used for HTML display(AH)
    for skill in resourceSkills:
              
        sID = str(skill.skillID)
        skill_ID.append(sID[:1])
        skill_Name.append(skill.skillID.skillName)
        skill_Points.append(str(skill.questionSkillPoints))
               
        count+=1
                                                    
    return zip(range(1,count),skill_ID,skill_Name, skill_Points)  

def getCourseSkills(course):
    # Fetch the skills for this course from the database.
    course_skills = CoursesSkills.objects.filter(courseID=course)

    skill_list = []

    for s in course_skills:
        skillDict = {}
        skillDict['id']=s.skillID.skillID
        skillDict['name']=s.skillID.skillName
        skill_list.append(skillDict)
        
    return skill_list

def getSkillsForQuestion(course,question):
    qskills = QuestionsSkills.objects.filter(questionID = question, courseID=course)
    
    skill_list = []
    
    for qskill in qskills:
        skill = {}
        skill['name'] = qskill.skillID.skillName
        skill['id'] = qskill.skillID.skillID
        skill['value'] = qskill.questionSkillPoints
        skill_list.append(skill)
    logger.debug(skill_list)
    return skill_list

def getTopicsForChallenge(challenge):
    challTopics = ChallengesTopics.objects.filter(challengeID=challenge)
    topics = []
    for t in challTopics:
        topic = {}
        topic['tag'] = t.topicID.topicName
        topic['id'] = t.topicID.topicID
        topics.append(topic)

    logger.debug("Topics To JSON: " + json.dumps(topics))

    return json.dumps(topics)

def autoCompleteTopicsToJson(currentCourse):
    topics = {}
    createdTopics = []
    course_topics = CoursesTopics.objects.filter(courseID=currentCourse)   
    for ct in course_topics:
        if ct.topicID.topicName != unspecified_topic_name:
            topics[ct.topicID.topicName] = None
            createdTopics.append({'tag': ct.topicID.topicName, 'id': ct.topicID.topicID})

    logger.debug("Auto Topics To JSON: " + json.dumps(topics))
    logger.debug("Created Topics: " + json.dumps(createdTopics))
    return json.dumps(topics), json.dumps(createdTopics)

def addSkillsToQuestion(course,question,skills,points):
    pointsDict = {}
    for (skillID,point) in zip(skills,points):
        pointsDict[skillID] = point
    qskills = QuestionsSkills.objects.filter(questionID = question, courseID=course)
    existingIDs = [qsk.skillID.skillID for qsk in qskills]
    deletionIDs = [id for id in existingIDs if id not in skills]
    newIDs = [id for id in skills if id not in existingIDs]
    overlappingIDs = [id for id in skills if id in existingIDs]
    
    QuestionsSkills.objects.filter(questionID = question, skillID__in=deletionIDs).delete()
    
    for id in newIDs:
        newQSkill = QuestionsSkills()
        newQSkill.questionID = question
        newQSkill.courseID = course
        newQSkill.skillID = Skills.objects.get(pk=id)
        newQSkill.questionSkillPoints = pointsDict[id]
        newQSkill.save()
        
    for qsk in qskills:
        id = qsk.skillID.skillID
        if id in overlappingIDs:
            if qsk.questionSkillPoints != pointsDict[id]:
                qsk.questionSkillPoints = pointsDict[id]
                qsk.save()
                
def addTopicsToChallenge(challenge, topics, unspecified_topic, currentCourse):
    
    logger.debug("[POST] t: " + str(topics))
    tops = json.loads(topics)
    tops = [dict(t) for t in set([tuple(d.items()) for d in tops])]
    logger.debug("[POST] topics: " + str(tops))
    challTopics = ChallengesTopics.objects.filter(challengeID = challenge)    

    if len(tops) > 0 and challTopics.exists():
        newTopicsIDs = [topic["id"] for topic in tops]
        existingIDs = [cTp.topicID.topicID for cTp in challTopics]
        deletionIDs = [id for id in existingIDs if id not in newTopicsIDs]
        newIDs = [id for id in newTopicsIDs if id not in existingIDs]
        logger.debug("[POST] " + str(newTopicsIDs) + " " + str(existingIDs) + " " + str(deletionIDs) + " " + str(newIDs))
        ChallengesTopics.objects.filter(topicID__in=deletionIDs, challengeID = challenge.challengeID).delete()

        for topic in tops:
            if topic['id'] in newIDs and topic['id'] != -1:
                newChallTopics = ChallengesTopics()
                newChallTopics.challengeID = challenge
                newChallTopics.topicID = Topics.objects.get(pk=topic['id'])
                newChallTopics.save()
                continue
            if topic['id'] in newIDs:
                newTopic = Topics()           
                newTopic.topicName = topic['tag']                   
                newTopic.save()

                courseTopic = CoursesTopics()
                courseTopic.topicID = newTopic
                courseTopic.courseID = currentCourse
                courseTopic.topicPos = 1
                courseTopic.save()

                newChallTopics = ChallengesTopics()
                newChallTopics.challengeID = challenge
                newChallTopics.topicID = newTopic
                newChallTopics.save()
    else:
        if challTopics.exists():
            for topic in challTopics:
                topic.delete()
        if len(tops) > 0:
            for topic in tops:
                if topic['id'] != -1:
                    newChallTopics = ChallengesTopics()
                    newChallTopics.challengeID = challenge
                    newChallTopics.topicID = Topics.objects.get(pk=topic['id'])
                    newChallTopics.save()
        else:
            challTopic = ChallengesTopics()
            challTopic.challengeID = challenge
            challTopic.topicID = unspecified_topic
            challTopic.save()
# Sets up the logged_in, username, and course_Name entries in the context_dict and then returns it along with the currentCourse if any.
def initialContextDict(request):
    context_dict = {}
    context_dict["logged_in"] = request.user.is_authenticated
    if request.user.is_authenticated:
        context_dict["username"] = request.user.username
        
    if 'currentCourseID' in request.session:
        currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
        context_dict['course_Name'] = currentCourse.courseName
    else:
        currentCourse = None
        context_dict['course_Name'] = 'Not Selected'
        
    context_dict['ccparams'] = CourseConfigParams.objects.get(courseID=currentCourse)
        
    return (context_dict,currentCourse)

def utcDate(date="None", form="%Y-%m-%d %H:%M:%S.%f"):
    ''' Converts date str to datetime.datetime object with utc timezone.
        Method should be used before storing dates in DateTimeField.
    '''
    
    if date == "None":
        dt = datetime.now(tz=timezone.utc).replace(microsecond=0)
        print("Current UTC: ", dt)
        return dt
    
    dt = datetime.strptime(date, form)
    
    print("Converted Time to UTC: " , dt.replace(tzinfo=timezone.utc))
    return dt.replace(tzinfo=timezone.utc)  

def localizedDate(request, date_str, date_format):
    tz = pytz.timezone(request.session['django_timezone'])
    
    return tz.localize(datetime.strptime(date_str, date_format))

