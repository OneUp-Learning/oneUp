
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from Instructors.models import Challenges, CoursesSkills, ChallengesTopics, CoursesTopics
from Instructors.views.utils import initialContextDict
from Students.models import StudentChallenges, StudentCourseSkills, StudentRegisteredCourses
from oneUp.decorators import instructorsCheck  
from Instructors.constants import unassigned_problems_challenge_name
    
@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='')
def classAchievementsViz(request):

    context_dict, currentCourse = initialContextDict(request)
    
    serious = 0
    warmUp = 0
    skills = 0
    if 'serious' in request.GET:
        serious = 1
        context_dict['serious']= 1
    elif 'warmUp' in request.GET:
        warmUp = 1
        context_dict['warmUp']= 1
    else:
        skills = 1
        context_dict['skills']= 1   
        
    st_crs = StudentRegisteredCourses.objects.filter(courseID=currentCourse).exclude(studentID__isTestStudent=True)                
    students = []                                         
    for st_c in st_crs:
        students.append(st_c.studentID)     # all students in the course
            
    if  skills:
        # visualize skills 
        skillNames = [] 
        allStudSkillPoints = []  
                             
        # for each skill, for each student
        c_skills = CoursesSkills.objects.filter(courseID=currentCourse)            
        for c_skill in c_skills: 
            skill = c_skill.skillID
            skillNames.append(skill.skillName)
            userNames = []
            userSkillPoints = []            

            for student in students: 
                userNames.append(str(student.user.first_name+' '+student.user.last_name))                    
                studentSkill = StudentCourseSkills.objects.filter(studentChallengeQuestionID__studentChallengeID__studentID=student, skillID=skill)
                if not studentSkill:
                    userSkillPoints.append(0)    
                else:
                    totalPointsSkill = 0
                    chall_question_IDs = []
                    print(studentSkill)
                    for s_skill in studentSkill:
                        print('s_skill')
                        print(s_skill)
                        chall_question_IDs.append(s_skill.studentChallengeQuestionID.questionID.questionID)  # all takings of contributing questions
                    
                    print('chall_question_IDs: ')
                    print(chall_question_IDs)    
                    q_set = set(chall_question_IDs)
                    print('q_set: ')
                    print(q_set)                         
                    q_answering = []    
                    for q in q_set:
                        #filter all answers of q
                        for s_skill in studentSkill:
                            if s_skill.studentChallengeQuestionID.questionID.questionID == q:
                                q_answering.append(s_skill.skillPoints)     
                        
                        print('max(q_answers): '+str(max(q_answering)))# adding the max of skill points from all answering of the same question q                                                    
                        totalPointsSkill +=max(q_answering)
                    
                    print('totalPointsSkill: '+str(totalPointsSkill))    
                    userSkillPoints.append(totalPointsSkill)     
       
            allStudSkillPoints.append(zip(userNames, userSkillPoints ))
            print(userNames)
            print(userSkillPoints)
                
        context_dict['skillsRange'] = zip(range(1,len(skillNames)+1),skillNames)
        context_dict['pointsRange'] = zip(range(1,len(skillNames)+1),allStudSkillPoints)
        context_dict['skillsCount'] = len(skillNames)
        print(skillNames)
        print(str(len(skillNames)))
        
        return render(request,'Instructors/ClassSkillsViz.html', context_dict)

    else:
        # visualize challenges               
        allChallengGrades = []
                            
        #Displaying the list of challenges from database
        if serious:
            challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=True).exclude(challengeName=unassigned_problems_challenge_name)
        else:
            ##mystical code that does the impossible task of joining two intersection tables
            ##then ordering by the content of the second intersection table             
            courses_topics_by_topic_pos = CoursesTopics.objects.filter(courseID=currentCourse).order_by('topicPos')
            topic_ids = []
            challenges_by_topic = []
            for courses_topic in courses_topics_by_topic_pos:
                topic_ids.append(courses_topic.topicID)

            for topic_ids in topic_ids:
                challenges_by_topic.append(ChallengesTopics.objects.filter(topicID=topic_ids, challengeID__courseID=currentCourse, challengeID__isGraded=False).exclude(challengeID__challengeName=unassigned_problems_challenge_name).order_by('challengeID__challengePosition'))


            challenges__objects_ordered_by_topic = []
            
            for challenge_by_topic in challenges_by_topic:
                for challenges_topic in challenge_by_topic:
                    challenges__objects_ordered_by_topic.append(challenges_topic.challengeID)

            
            challenges = challenges__objects_ordered_by_topic
            ##challenges = Challenges.objects.filter(courseID=currentCourse, isGraded=False).exclude(challengeName=unassigned_problems_challenge_name)
                             
        for challenge in challenges:
#            userScores = []
#            userEarliestScores = []
            maxTestScores = []
            mediumTestScores = []
            minTestScores = []
            userNames = []
            challNames = [] 
                       
            if StudentChallenges.objects.filter(courseID=currentCourse, challengeID = challenge):   
                
                for student in students:
                    if StudentChallenges.objects.filter(studentID=student, courseID=currentCourse, challengeID = challenge):
                        studentChall = StudentChallenges.objects.filter(studentID=student, courseID=currentCourse, challengeID = challenge) 

#                         latestChall = StudentChallenges.objects.filter(studentID=student, courseID=currentCourse, challengeID = challenge).latest('startTimestamp')
#                         earliestChall =  StudentChallenges.objects.filter(studentID=student, courseID=currentCourse, challengeID = challenge).earliest('startTimestamp')
#                                                 
#                         if challenge.isGraded:    # serious challenge, add the adjustment + curve
#                             userLatestScore = latestChall.getScore()
#                             userEarliestScore = earliestChall.getScore()
#                         else:
#                             userLatestScore = latestChall.testScore         # warmup challenge
#                             userEarliestScore = earliestChall.testScore
#                                                                                         
#                         userScores.append(userLatestScore)
#                         userEarliestScores.append(userEarliestScore)
                                               
                        userNames.append(str(student.user.first_name+' '+student.user.last_name))
                        challNames.append(challenge.challengeName)
                        userGradeID  = []                    
                        sumScores = 0
                        for scr in studentChall:
                            if challenge.isGraded:    # serious challenge, add the adjustment + curve
                                score = scr.getScore()
                            else:
                                score = scr.testScore         # warmup challenge
                            
                            #userGradeID.append(int(scr.testScore))
                            userGradeID.append(int(score))
                            sumScores += int(score)
                        
                        maxTestScores.append(max(userGradeID))
                        minTestScores.append(min(userGradeID))
                        mediumTestScores.append(sumScores/len(studentChall))

                        allChallengGrades.append(zip(challNames, userNames, maxTestScores,mediumTestScores, minTestScores ))        
        
        context_dict['challengesRange'] = zip(range(1,len(allChallengGrades)+1),allChallengGrades)
        context_dict['challengesCount'] = len(challenges)
                                
    return render(request,'Instructors/ClassAchievementsViz.html', context_dict)
