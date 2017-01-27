#import nltk
from Instructors.models import Tags, Skills, ChallengeTags, ResourceTags, QuestionsSkills, Topics, ChallengesTopics
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
                
            print ("in utils:  end of split list")
            
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

def saveChallengesTopics(topicstring, challenge):        #10/01/2015

        #if topicstring is not null or empty
        if not topicstring == "":
            
            # delete all previous topics for this challenge and course
            resourceTopics = ChallengesTopics.objects.filter(challengeID = challenge.challengeID).delete()
                
            #split string into an array 
            topicsList = topicstring.split(',')
            
            #Break the elements in topicsList of name
            for topic in topicsList:
                topicName  = topic.strip()
                
                # find the skillID for this skillName
                for t in Topics.objects.all():
                    print(t.topicName)
                    if topicName == t.topicName:
                        topicID = t.topicID
                        print(topicID)
                              
                # now add the new topic for this challenge                 
                # create a new topic-challenge object              
                newCTopicsObject = ChallengesTopics()
                newCTopicsObject.challengeID = challenge
                newCTopicsObject.topicID = Topics(topicID)                
               
                newCTopicsObject.save()
        else:
            # delete all previous skill for this question and course                    
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
     
    skillstring = ""
    commaCheck = False

    for skill in resourceSkills:
        #split tag string to get just tag ID
        if commaCheck:
            skillstring = str(skillstring + ", ")  
        skillName = skill.skillID.skillName
        skillpoints = str(skill.questionSkillPoints)
        skillstring = str(skillstring + skillName + " (" + skillpoints+ ")")        
        commaCheck = True 
                                                    
    return skillstring    

def extractTopics(resource, resourceIndicator):   

    if resourceIndicator == "challenge":
        resourceTopics = ChallengesTopics.objects.filter(challengeID = resource.challengeID)
     
    topicstring = ""
    commaCheck = False

    for topic in resourceTopics:
        if commaCheck:
            topicstring = str(topicstring + ", ")  
        topicName = topic.topicID.topicName
        topicstring = str(topicstring + topicName)        
        commaCheck = True 
                                                    
    return topicstring      
                           