#import nltk
from Instructors.models import Tags, Skills, ChallengeTags, ResourceTags, QuestionsSkills, Topics, ChallengesTopics
from Instructors.constants import unspecified_topic_name
import re
import string
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
                                        
def saveChallengeTags(tagString, challenge):        #DD 02/24/2015

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
            
            for tagWord in tagsList2:
                
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
            resourceTags = ChallengeTags.objects.filter(challengeID = challenge.challengeID).delete()
                
            # now add the new tags for this challenge 
            for tagWord in tagsList2:                 
                #create a new tag-challenge object              
                newTagsObject = ChallengeTags()
                newTagsObject.challengeID = challenge
                
                # find tagID
                for tempTag in Tags.objects.all():
                    if tempTag.tagName == tagWord:
                        newTagsObject.tagID = Tags(tempTag.tagID)
                        break                
               
                newTagsObject.save()
                print (str("Tagid: ") + str(newTagsObject.tagID))   
                             
                                
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

def saveChallengesTopics(topicstring, challenge):        

        #if topicstring is not null or empty
        if not topicstring == "":
            
            # delete all previous topics for this challenge and course
            resourceTopics = ChallengesTopics.objects.filter(challengeID = challenge.challengeID).delete()
                
            #split string into an array 
            topicsList = topicstring.split(',')
            print(topicsList)
            
            topicNames = set()
            for topic in topicsList:
                if not topic == '':
                    topicNames.add(topic.strip())
            print(topicNames)
            
            # remove duplicates
            #uniqueTopicNames = set(topicNames)
            if len(topicNames) > 1:
                topicNames.discard(unspecified_topic_name)
                print(topicNames)
            for topicName in topicNames:
                print(topicName)               
                topic = Topics.objects.filter(topicName=topicName)               

                # now add the new topic for this challenge                              
                newCTopicsObject = ChallengesTopics()
                newCTopicsObject.challengeID = challenge
                newCTopicsObject.topicID = topic[0]              
                newCTopicsObject.save()
        else:
            # delete all previous topics for this challenge                    
            resourceTopics = ChallengesTopics.objects.filter(challengeID = challenge.challengeID).delete()               
                                                                
def extractTags(resource, resourceIndicator):   

    if resourceIndicator == "question":
        resourceTags = ResourceTags.objects.filter(questionID = resource.questionID)
    else:
        # "challenge"
        resourceTags = ChallengeTags.objects.filter(challengeID = resource.challengeID)
     
    tagstring = ""
    commaCheck = False

    for tag in resourceTags:
        #split tag string to get just tag ID
#         tagSplit = str(tag.tagID).split(",")
#         tagID = int(tagSplit[0])
                    
        if commaCheck:
            tagstring = str(tagstring + ",")
        #holds tag record
#         tempTag = Tags.objects.get(pk=int(tagID))
#         tagstring = str(tagstring + tempTag.tagName)
        tagName = tag.tagID.tagName
        tagstring = str(tagstring + tagName)        
  
        commaCheck = True                                        
        
    return tagstring  

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

def extractTopics(resource, resourceIndicator):   

    if resourceIndicator == "challenge":
        resourceTopics = ChallengesTopics.objects.filter(challengeID = resource.challengeID)
     
    topic_ID = []
    topic_Name = []
    count = 1
    for topic in resourceTopics: 
        topic_ID.append(topic.topicID)        
        topic_Name.append(topic.topicID.topicName)
        count+= 1
                                                    
    return zip(range(1, count), topic_ID, topic_Name)      
                                                      