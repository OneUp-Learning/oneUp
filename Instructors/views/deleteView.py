'''
Created on Apr 9, 2014
Updated 02/28/2015

@author: dichevad, irwink
'''
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.contrib.auth.models import User
from Students.models import StudentBadges, StudentEventLog, Student

from Instructors.models import Questions, Courses, Challenges, Skills, ChallengesQuestions, Topics, Announcements, Activities, Milestones

from django.contrib.auth.decorators import login_required

@login_required
def deleteQuestion(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict = { }

    if request.POST:

        # If there's an existing question, we wish to edit it.  If new question,
        # create a new Question object.
        try:
            if request.POST['questionId']:
                question = Questions.objects.get(pk=int(request.POST['questionId']))            
                message = "Question #"+str(question.questionID)+ " "+question.preview+" successfully deleted"
                question.delete()
        except Questions.DoesNotExist:
            message = "There was a problem deleting Question #"+str(question.questionID)+ " "+question.preview

        context_dict['message']=message

        
    return redirect('/oneUp/instructors/questionList', context_dict)
def deleteQuestionFromChallenge(request):           # 02/28/2015  
    
 
    context_dict = { }

    if request.POST:

        # Delete only the record in the ChallengesQuestions(models.Model)  
        try:
            if request.POST['questionId']:              
                challenge_question = ChallengesQuestions.objects.filter(challengeID=request.POST['challengeID']).filter(questionID=request.POST['questionId'])
                for cq in challenge_question:
                    points=cq.points
                question = Questions.objects.get(pk=int(request.POST['questionId']))           
                message = "Question #"+str(question.questionID)+ " "+question.preview+" successfully deleted from Challenge "
                challenge_question.delete()
                unassign = 0
                
            # Check if this question does not appears in another challenge - then add it to Unassigned Problem list
            if not ChallengesQuestions.objects.filter(questionID = question.questionID):
                currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
                chall=Challenges.objects.filter(challengeName="Unassigned Problems",courseID=currentCourse)
                for challID in chall:
                    challengeID = challID.challengeID
                challenge = Challenges.objects.get(pk=int(challengeID))
                print(request.POST['challengeID'])
                print(challengeID)
                
                #Check if unassigned problem list is deleting the question, if it is then delete it
                #if is not then save the question in unassigned problem list
                if (int(request.POST['challengeID']) == int(challengeID)):
                    question.delete()
                    unassign =1
                else:
                    ChallengesQuestions.addQuestionToChallenge(question, challenge,points)
                    
                           
        except Questions.DoesNotExist:
            message = "There was a problem deleting Question #"+str(question.questionID)+ " "+question.preview

        context_dict['message']=message
        
        challengeID = request.POST['challengeID']
 
    #return redirect('/oneUp/instructors/challengeEditQuestions?challengeID=' + challengeID, context_dict)
    if unassign ==1:
        return redirect('/oneUp/instructors/challengeQuestionsList?problems', context_dict)
    else:
        return redirect('/oneUp/instructors/challengeQuestionsList?challengeID=' + challengeID, context_dict)

def deleteChallenge(request):
    # Request the context of the request. 
    # The context contains information such as the client's machine details, for example.
 
    context_dict = { }

    if request.POST:

        # If there's an existing question, we wish to edit it.  If new question,
        # create a new Question object.
        try:
            if request.POST['challengeID']:
                challenge = Challenges.objects.get(pk=int(request.POST['challengeID']))            
                message = "Challenge #"+str(challenge.challengeID)+ " "+challenge.challengeName+" successfully deleted"
                
                #Get the ID for Unassigned Problems challenge
                currentCourse = Courses.objects.get(pk=int(request.session['currentCourseID']))
                uChallenge=Challenges.objects.filter(challengeName="Unassigned Problems",courseID=currentCourse)
                for challID in uChallenge:
                    uChallengeID = challID.challengeID
                cID = Challenges.objects.get(pk=int(uChallengeID))
                
                #Get the ID and point for the questions associated with the challenge that we want to delete
                challenge_question = ChallengesQuestions.objects.filter(challengeID=request.POST['challengeID'])
                for cq in challenge_question:
                    qId = cq.questionID
                    qPoint = cq.points
                    
                    #Counts how many times, the questions of the challenge that we want to delete, are associate in any challenges
                    #The count also counts the challenge that we want to delete
                    countCQ=ChallengesQuestions.objects.filter(questionID = cq.questionID.questionID)
                    num_challenges = countCQ.count()

                    #If the count is equal to one (meaning that is only associate with the challenge that we want to delete)
                    #Then we want to save the question at Unassign Question challenge
                    if num_challenges == 1:
                        ChallengesQuestions.addQuestionToChallenge(qId, cID,qPoint)

                #Now that we check the question associate with this challenge, we can delete it
                challenge.delete()
                
        except Challenges.DoesNotExist:
            message = "There was a problem deleting Challenge #"+str(challenge.challengeID)+ " "+challenge.challengeName

        context_dict['message']=message
    
    if 'warmUp' in request.GET:
        return redirect('/oneUp/instructors/challengesList?warmUp', context_dict)
    else:
        return redirect('/oneUp/instructors/challengesList', context_dict)

def deleteSkill(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict = { }
    print (str('got here'))
    if request.POST:

        # If there's an existing question, we wish to edit it.  If new question,
        # create a new Question object.
        try:
            if request.POST['skillID']:
                skill = Skills.objects.get(pk=int(request.POST['skillID']))  
                print(skill)          
                message = "skill #"+str(skill.skillID)+ " "+skill.skillName+" successfully deleted"
                skill.delete()
        except Skills.DoesNotExist:
            message = "There was a problem deleting Skill #"+str(skill.skillID)+ " "+skill.skillName

        context_dict['message']=message
        
    return redirect('/oneUp/instructors/skillsList', context_dict)

def deleteUser(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict = { }
    print(str('got here for delete user'))
    if request.POST:

        # If there's an existing question, we wish to edit it.  If new question,
        # create a new Question object.
        try:
            if request.POST['userID']:
                u = User.objects.get(username=request.POST['userID']) 
                print(u)   
                message = "User "+str(u.first_name)+ " "+str(u.last_name)+" was successfully deleted"
                u.delete()

#                 studentEventLog = StudentEventLog.objects.filter(student = u)
#                 for sEventLog in studentEventLog:
#                     sEventLog.delete()
#                 print 'delete student event log'   
                        
        except User.DoesNotExist:
            message = "There was a problem deleting user #"

        context_dict['message']=message
        
    return redirect('/oneUp/instructors/createStudentListView', context_dict)

def deleteTopic(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict = { }
    print (str('got here'))
    if request.POST:

        # If there's an existing question, we wish to edit it.  If new question,
        # create a new Question object.
        try:
            if request.POST['topicID']:
                topic = Topics.objects.get(pk=int(request.POST['topicID']))  
                print(topic)          
                message = "topic #"+str(topic.topicID)+ " "+topic.topicName+" successfully deleted"
                topic.delete()
        except Topics.DoesNotExist:
            message = "There was a problem deleting Topic #"+str(topic.topicID)+ " "+topic.topicName

        context_dict['message']=message
        
    return redirect('/oneUp/instructors/topicsList', context_dict)

def deleteActivity(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict = { }

    if request.POST:
        print("Deleting Activity")
        # If there's an existing question, we wish to edit it.  If new question,
        # create a new Question object.
        try:
            if request.POST['activityID']:
                activity = Activities.objects.get(pk=int(request.POST['activityID']))            
                message = "Activity #"+str(activity.activityID)+ ": "+str(activity.activityID) + "was successfully deleted"
                activity.delete()
        except Activities.DoesNotExist:
            message = "There was a problem deleting Activity #"+str(activity.activityID)

        context_dict['message']=message
        
    return redirect('/oneUp/instructors/activitiesList', context_dict)

def deleteAnnouncement(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict = { }

    if request.POST:

        # If there's an existing question, we wish to edit it.  If new question,
        # create a new Question object.
        try:
            if request.POST['announcementID']:
                announcement = Announcements.objects.get(pk=int(request.POST['announcementID']))            
                message = "Announcement #"+str(announcement.announcementID)+ " created by "+str(announcement.authorID)+ " on " + str(announcement.startTimestamp) + "was successfully deleted"
                announcement.delete()
        except Announcements.DoesNotExist:
            message = "There was a problem deleting Announcement #"+str(announcement.announcementID)

        context_dict['message']=message
        
    return redirect('/oneUp/instructors/announcementList', context_dict)

def deleteMilestone(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
 
    context_dict = { }

    if request.POST:

        # If there's an existing question, we wish to edit it.  If new question,
        # create a new Question object.
        try:
            if request.POST['milestoneID']:
                milestone = Milestones.objects.get(pk=int(request.POST['milestoneID']))            
                message = "Milestone #"+str(milestone.milestoneID)+ ": "+str(milestone.milestoneID) + "was successfully deleted"
                milestone.delete()
        except Milestones.DoesNotExist:
            message = "There was a problem deleting Milestone #"+str(milestone.milestoneID)

        context_dict['message']=message
        
    return redirect('/oneUp/instructors/milestonesList', context_dict)