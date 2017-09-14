'''
Created on Oct 19, 2016

Modified 

@author: Austin Hodge
'''
from django.template import RequestContext
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Instructors.models import Announcements, Instructors, Courses, Challenges
from time import strftime

def createContextForUpcommingChallengesList(currentCourse, context_dict):
    chall_ID = []      
    chall_Name = []         
    start_Timestamp = []
    end_Timestamp = []
    UnassignID = 0
        
    # Filter challenges to show only Graded(Serious Challenges) and sort by earlier dates first
    challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=True).order_by('endTimestamp')
    currentTime = strftime("%Y-%m-%d %H:%M:%S")
    
    index = 0
    for item in challenges:
        if index < 3 and item.isVisible: # Showing first three upcomming assignments
            # Check if current time is within the start and end time of the challenge
            if currentTime > item.startTimestamp.strftime("%Y-%m-%d %H:%M:%S"):
                if currentTime < item.endTimestamp.strftime("%Y-%m-%d %H:%M:%S"):
                    chall_ID.append(item.challengeID) #pk
                    chall_Name.append(item.challengeName)
                    start_Timestamp.append(item.startTimestamp)
                    end_Timestamp.append(item.endTimestamp)
                    index += 1
               
    # The range part is the index numbers.
    context_dict['challenge_range'] = zip(range(1,challenges.count()+1),chall_ID,chall_Name,start_Timestamp,end_Timestamp)  ##,chall_Category
    return context_dict
