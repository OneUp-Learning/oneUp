#import nltk
from Instructors.models import CoursesTopics, Tags, Skills, ChallengeTags, ResourceTags, QuestionsSkills, Topics, ChallengesTopics, CoursesSkills, Courses
from Instructors.constants import unspecified_topic_name
from Badges.models import CourseConfigParams
import re
import string
from django.contrib.auth.decorators import login_required
from oneUp.logger import logger
import json

@login_required
def saveTags(tagString, resource, resourceIndicator):

        #if tagString is not null or empty
        if not tagString == "":
            
            #split string into an array 
            tagsList = tagString.split(',') 
            
            tagsList2 = []
            # Removes whitespaces and disregards empty tags
            for tword in tagsList:
                tword = tword.strip()
                if tword != "":
                    tagsList2.append(tword)   
            print ("in utils:  end of split list")
            
            for tagWord in tagsList2:
                tagExists = False  #used to check if a tag exists already
                
                #create a new tag-object; check what is tagged object - question or challenge               
                if resourceIndicator == "question":
                    newTagsObject = ResourceTags()
                elif resourceIndicator == "challenge":
                    newTagsObject = ChallengeTags()
               
                #if the tag already exists... set tagExists to 1
                for item in Tags.objects.all():
                    if tagWord == str(item.tagName):
                        tagExists = True
                        break

                if not tagExists:
                    #create new tag                    
                    newTag = Tags()
                    newTag.tagName = tagWord
                    newTag.save()
   
                for tempTag in Tags.objects.all():
                    if tempTag.tagName == tagWord:
                        #check if there is such tag for this resource
                        
                        newTagsObject.tagID = Tags(tempTag.tagID)
                        print (str("Tagid: ") + str(tempTag.tagID))
                        break
                
                if resourceIndicator == "question":
                    newTagsObject.questionID = resource
                    print (str("questionID: ") + str(newTagsObject.questionID))
                    print (str(newTagsObject.questionID))
                    newTagsObject.save()
                elif resourceIndicator == "challenge":
                    newTagsObject.challengeID = resource
                    newTagsObject.save()

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
                                        
def saveChallengeTags(tagString, challenge): 

    tags = json.loads(tagString)
    logger.debug("[POST] tags: " + str(tags))
    newTags = [tag['tag'] for tag in tags]
    if len(tags) > 0:
        tagExists = False  #used to check if a tag exists already  
        for tag in newTags:                            
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
    resourceTags = ChallengeTags.objects.filter(challengeID = challenge.challengeID).delete()
        
    # now add the new tags for this challenge 
    for tag in newTags:                 
        #create a new tag-challenge object              
        newTagsObject = ChallengeTags()
        newTagsObject.challengeID = challenge
        # find tagID
        for tempTag in Tags.objects.all():
            if tempTag.tagName == tag:
                newTagsObject.tagID = Tags(tempTag.tagID)
                break                
        newTagsObject.save()
                                
def saveQuestionTags(tagString, question):        #DD 02/24/2015

        #if tagString is not null or empty
        if not tagString == "":
            
            #split string into an array 
            tagsList = tagString.split(',') 
            tagsList2 = []
            # Removes whitespaces and disregards empty tags
            for tword in tagsList:
                tword = tword.strip()
                if tword != "":
                    tagsList2.append(tword)
            print ("in utils:  end of split list")
            
            for tagWord in tagsList2:
                
                # Removing leading and trailing spaces
                tagWord = tagWord.strip()

                tagExists = False  #used to check if a tag exists already                              
                for item in Tags.objects.all():
                    if tagWord == str(item.tagName):
                        tagExists = True
                        break

                if not tagExists:
                    #create new tag                    
                    newTag = Tags()
                    newTag.tagName = tagWord
                    newTag.save()
   
            # delete all previous tags for this challenge
            resourceTags = ResourceTags.objects.filter(questionID = question.questionID).delete()
                
            # now add the new tags for this challenge 
            for tagWord in tagsList2:                 
                #create a new tag-challenge object              
                newTagsObject = ResourceTags()
                newTagsObject.questionID = question
                
                # find tagID
                for tempTag in Tags.objects.all():
                    if tempTag.tagName == tagWord:
                        newTagsObject.tagID = Tags(tempTag.tagID)
                        break                
               
                newTagsObject.save()
                print (str("Tagid: ") + str(newTagsObject.tagID))                

def saveQuestionSkills(skillstring, question, challenge):        #03/18/2015

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
                createdSkill = QuestionsSkills.objects.filter(skillID = skillID, questionID = question.questionID, challengeID = challenge.challengeID)
                
                if (createdSkill):
                    # Update skill with the new skillPoints (AH)
                    skillObj = createdSkill[0]
                    skillObj.questionSkillPoints = int(skillPoints)
                    skillObj.save()
                else:              
                    # create a new skill-question object
                    newQSkillsObject = QuestionsSkills()
                    newQSkillsObject.questionID = question
                    newQSkillsObject.challengeID = challenge
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
        skillDict['ID']=s.skillID.skillID
        skillDict['name']=s.skillID.skillName
        skill_list.append(skillDict)
        
    return skill_list

def getSkillsForQuestion(challenge,question):
    qskills = QuestionsSkills.objects.filter(questionID = question, challengeID=challenge)
    
    skill_list = []
    
    for qskill in qskills:
        skillDict = {}
        skillDict['name'] = qskill.skillID.skillName
        skillDict['ID'] = qskill.skillID.skillID
        skillDict['value'] = qskill.questionSkillPoints
        skill_list.append(skillDict)
        
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
            topics[ct.topicID.topicName] = ''
            createdTopics.append({'tag': ct.topicID.topicName, 'id': ct.topicID.topicID})

    logger.debug("Auto Topics To JSON: " + json.dumps(topics))
    logger.debug("Created Topics: " + json.dumps(createdTopics))
    return json.dumps(topics), json.dumps(createdTopics)

def addSkillsToQuestion(challenge,question,skills,points):
    pointsDict = {}
    for (skillID,point) in zip(skills,points):
        pointsDict[skillID] = point
    qskills = QuestionsSkills.objects.filter(questionID = question, challengeID=challenge)
    existingIDs = [qsk.skillID.skillID for qsk in qskills]
    deletionIDs = [id for id in existingIDs if id not in skills]
    newIDs = [id for id in skills if id not in existingIDs]
    overlappingIDs = [id for id in skills if id in existingIDs]
    
    QuestionsSkills.objects.filter(questionID = question, skillID__in=deletionIDs).delete()
    
    for id in newIDs:
        newQSkill = QuestionsSkills()
        newQSkill.questionID = question
        newQSkill.challengeID = challenge
        newQSkill.skillID = Skills.objects.get(pk=id)
        newQSkill.questionSkillPoints = pointsDict[id]
        newQSkill.save()
        
    for qsk in qskills:
        id = qsk.skillID.skillID
        if id in overlappingIDs:
            if qsk.questionSkillPoints != pointsDict[id]:
                qsk.questionSkillPoints = pointsDict[id]
                qsk.save()
                
def addTopicsToChallenge(challenge, topics, unspecified_topic):
    
    tops = json.loads(topics)
    logger.debug("[POST] topics: " + str(tops))
    if len(tops) > 0:
        newTopicsIDs = [topic["id"] for topic in tops]

        challTopics = ChallengesTopics.objects.filter(challengeID = challenge.challengeID)
        existingIDs = [cTp.topicID.topicID for cTp in challTopics]
        deletionIDs = [id for id in existingIDs if id not in newTopicsIDs]
        newIDs = [id for id in newTopicsIDs if id not in existingIDs]

        ChallengesTopics.objects.filter(topicID__in=deletionIDs).delete()
        
        for id in newIDs:
            newChallTopics = ChallengesTopics()
            newChallTopics.challengeID = challenge
            newChallTopics.topicID = Topics.objects.get(pk=id)
            newChallTopics.save()
    else:
        challTopic = ChallengesTopics()
        challTopic.challengeID = challenge
        challTopic.topicID = unspecified_topic
        challTopic.save()
         
    
# Sets up the logged_in, username, and course_Name entries in the context_dict and then returns it along with the currentCourse if any.
def initialContextDict(request):
    context_dict = {}
    context_dict["logged_in"] = request.user.is_authenticated()
    if request.user.is_authenticated():
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
    from datetime import datetime, timezone
    
    if date == "None":
        dt = datetime.now(tz=timezone.utc).replace(microsecond=0)
        print("Current UTC: ", dt)
        return dt
    
    dt = datetime.strptime(date, form)
    
    print("Converted Time to UTC: " , dt.replace(tzinfo=timezone.utc))
    return dt.replace(tzinfo=timezone.utc)  
