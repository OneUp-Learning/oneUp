'''
Created on Oct 19, 2016

Modified 

@author: Austin Hodge
'''

from Instructors.models import Challenges
from Instructors.constants import default_time_str
from Instructors.views.utils import utcDate
from datetime import datetime

def createContextForUpcommingChallengesList(currentCourse, context_dict):
    chall_ID = []      
    chall_Name = []         
    start_Timestamp = []
    end_Timestamp = []
        
    # Filter challenges to show only Graded(Serious Challenges) and sort by earlier dates first
    challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=True).order_by('endTimestamp')
    currentTime = utcDate().strftime("%m/%d/%Y %I:%M %p") 
    index = 0
    for item in challenges:
        if index < 3 and item.isVisible: # Showing first three upcomming assignments
            # Check if current time is within the start and end time of the challenge and that the endtime is not the default for 'unchecked' endtime
            if currentTime > datetime.strptime(str(item.startTimestamp), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M %p"):
                if currentTime < datetime.strptime(str(item.endTimestamp), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M %p") and not datetime.strptime(str(item.endTimestamp), "%Y-%m-%d %H:%M:%S+00:00").strftime("%m/%d/%Y %I:%M:S %p") == default_time_str:
                    chall_ID.append(item.challengeID) #pk
                    chall_Name.append(item.challengeName)
                    start_Timestamp.append(item.startTimestamp)
                    end_Timestamp.append(item.endTimestamp)
                    index += 1
               
    # The range part is the index numbers.
    context_dict['challenge_range'] = zip(range(1,len(chall_ID)+1),chall_ID,chall_Name,start_Timestamp,end_Timestamp)  ##,chall_Category
    return context_dict