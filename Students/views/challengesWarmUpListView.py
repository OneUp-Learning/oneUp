'''
Created on Oct 1, 2015

@author: Alex
'''

from django.shortcuts import render
from django.utils import timezone
from Instructors.models import Topics, CoursesTopics, ChallengesTopics, Challenges, ChallengesQuestions
from Instructors.constants import unspecified_topic_name
from Students.models import StudentChallenges, StudentProgressiveUnlocking
from Students.views.utils import studentInitialContextDict
from Badges.enums import ObjectTypes
from Badges.models import ProgressiveUnlocking, CourseConfigParams
from django.db.models import Q
from Instructors.views.utils import localizedDate, current_localtime

from django.contrib.auth.decorators import login_required


def challengesForTopic(request, topic, student, currentCourse):
    challenge_ID = []
    isWarmup = []
    challenge_Name = []
    score = []
    chall_position = []
    isUnlocked = []
    ulockingDescript = []

    currentTime = current_localtime() # timezone.now() # TODONE: Use current localtime
    challenge_topics = ChallengesTopics.objects.filter(topicID=topic).order_by("challengeID__challengePosition").filter(Q(challengeID__startTimestamp__lt=currentTime) | Q(
        challengeID__hasStartTimestamp=False), Q(challengeID__endTimestamp__gt=currentTime) | Q(challengeID__hasEndTimestamp=False))
    if challenge_topics:
        for ct in challenge_topics:
            if Challenges.objects.filter(challengeID=ct.challengeID.challengeID, isGraded=False, isVisible=True, courseID=currentCourse):

                challQuestions = ChallengesQuestions.objects.filter(
                    challengeID=ct.challengeID.challengeID)

                if challQuestions:
                    challID = ct.challengeID.challengeID
                    challenge_ID.append(challID)
                    isWarmup.append(True)
                    challenge_Name.append(ct.challengeID.challengeName)
                    chall_position.append(ct.challengeID.challengePosition)

                    if StudentChallenges.objects.filter(studentID=student, courseID=currentCourse, challengeID=challID):
                        item = StudentChallenges.objects.filter(
                            studentID=student, courseID=currentCourse, challengeID=challID)
                        gradeID = []

                        for sc in item:
                            gradeID.append(sc.testScore)

                        # Calculation for ranking score by 3 levels (Above average, Average, Below Average)
                        tTotal = (sc.challengeID.totalScore/3)

                        # Above Average Score
                        if (max(gradeID) >= (2*tTotal)):
                            score.append(3)
                        # Average Score
                        elif (max(gradeID) > tTotal) and (max(gradeID) < (2*tTotal)):
                            score.append(4)
                        # Below Average Score
                        else:
                            score.append(5)
                    else:
                        score.append(2)  # no attempt

                    # pUnlocking check if not object then we assume there is no pUnlocking rule in place
                    studentPUnlocking = StudentProgressiveUnlocking.objects.filter(
                        studentID=student, objectID=ct.challengeID.challengeID, objectType=ObjectTypes.challenge, courseID=currentCourse).first()
                    if studentPUnlocking:
                        isUnlocked.append(studentPUnlocking.isFullfilled)
                        ulockingDescript.append(
                            studentPUnlocking.pUnlockingRuleID.description)
                    else:
                        isUnlocked.append(True)
                        ulockingDescript.append('')
    else:
        challenge_ID.append('')
        isWarmup.append(True)
        challenge_Name.append('')
        score.append(1)
        chall_position.append(0)

    # return sorted(list(zip(challenge_Name,challenge_ID,score,chall_position)), key=lambda tup: tup[4])
    return sorted(list(zip(range(1, challenge_topics.count()+1), challenge_Name, challenge_ID, isWarmup, score, chall_position, isUnlocked, ulockingDescript)), key=lambda tup: -tup[4])


@login_required
def ChallengesWarmUpList(request):
    # Request the context of the request.

    context_dict, currentCourse = studentInitialContextDict(request)

    if 'currentCourseID' in request.session:

        student = context_dict['student']

        if "taken" in request.GET:
            cc = CourseConfigParams.objects.get(courseID=currentCourse)
            if cc.classmatesChallenges and cc.calloutAfterWarmup:
                chall = Challenges.objects.get(
                    challengeID=int(request.GET["warmup_id"])).challengeID
                studentChall = StudentChallenges.objects.filter(
                    challengeID=chall)
                if studentChall.count() == 1:
                    if studentChall[0].testScore == studentChall[0].challengeID.totalScore:
                        context_dict["congrat"] = "It took you only one time to solve this. Great Job!"
                        cc = CourseConfigParams.objects.get(
                            courseID=currentCourse)
                        if cc.calloutAfterWarmup:
                            context_dict["calloutQ"] = "Would you like to call out your classmates?"
                            context_dict["student_chall_id"] = studentChall[0].studentChallengeID

        topic_ID = []
        topic_Name = []
        topic_Pos = []
        challenges_count = []
        all_challenges_for_topic = []
        isTopicUnlocked = []

        course_topics = CoursesTopics.objects.filter(
            courseID=currentCourse).order_by("topicPos")
        hasUnspecifiedTopic = False

        for ct in course_topics:

            tID = ct.topicID.topicID
            tName = Topics.objects.get(pk=tID).topicName
            if not tName == unspecified_topic_name:   # leave challenges with unspecified topic for last
                topic_ID.append(tID)
                topic_Name.append(tName)
                topic_Pos.append(str(ct.topicPos))
                topic_challenges = challengesForTopic(request, ct.topicID, student, currentCourse)
                challenges_count.append(len(list(topic_challenges)))
                all_challenges_for_topic.append(topic_challenges)

                # Progressive Unlocking for Topic
                unlockedTopic = StudentProgressiveUnlocking.objects.filter(
                    studentID=student, courseID=currentCourse, objectType=ObjectTypes.topic, objectID=ct.pk).first()
                if unlockedTopic:
                    isTopicUnlocked.append(
                        {'isFullfilled': unlockedTopic.isFullfilled, 'descript': unlockedTopic.pUnlockingRuleID.description})
                else:
                    isTopicUnlocked.append(
                        {'isFullfilled': True, 'descript': ''})
            else:
                unspecified_topic = ct.topicID
                hasUnspecifiedTopic = True

        # Add the challenges with unspecified topic at the end
        if hasUnspecifiedTopic:
            topic_ID.append(unspecified_topic.topicID)
            topic_Name.append("Miscellaneous")
            topic_Pos.append(str(len(topic_Pos)+1))
            topic_challenges = challengesForTopic(request, unspecified_topic, student, currentCourse)
            challenges_count.append(len(list(topic_challenges)))
            all_challenges_for_topic.append(topic_challenges)
            isTopicUnlocked.append({'isFullfilled': True, 'descript': ''})

        context_dict['isWarmup'] = True

        context_dict['topic_range'] = zip(range(1, course_topics.count(
        )+1), topic_ID, topic_Name, topic_Pos, challenges_count, all_challenges_for_topic, isTopicUnlocked)

    return render(request, 'Students/ChallengesWarmUpList.html', context_dict)
