'''
Created on Feb 25, 2019

@author: omar
'''

from django.shortcuts import redirect, render

from Badges.models import CourseConfigParams
from Instructors.models import ChallengesTopics, CoursesTopics, Topics
from Instructors.views.utils import initialContextDict
from Students.models import (DuelChallenges, Student, StudentChallenges,
                             StudentRegisteredCourses, Winners)


def duel_report(request):

    def get_duel_challenges_filter(filter_type, type_id, current_course, context_dict):

        if filter_type == 'topic':
            duel_challenges_raw = DuelChallenges.objects.filter(
                courseID=current_course)
            duel_challenges = []

            topics_raw = Topics.objects.filter(topicID=type_id)
            context_dict['duel_current_filter'] = 'Topic: ' + \
                topics_raw[0].topicName

            for duel_challenge_raw in duel_challenges_raw:
                chall_topics = ChallengesTopics.objects.filter(
                    topicID__topicID=type_id, challengeID=duel_challenge_raw.challengeID)
                if chall_topics:
                    duel_challenges.append(duel_challenge_raw)

        elif filter_type == 'student':
            duel_challenges_challenger = DuelChallenges.objects.filter(
                courseID=current_course, challenger__user__username=type_id)
            duel_challenges_challengee = DuelChallenges.objects.filter(
                courseID=current_course, challengee__user__username=type_id)
            duel_challenges = list(duel_challenges_challenger) + \
                list(duel_challenges_challengee)
            student = Student.objects.get(user__username=type_id)
            context_dict['duel_current_filter'] = 'Student: ' + \
                student.user.last_name

        elif filter_type == 'completeness_status':
            if type_id == 'not_started':
                duel_challenges = DuelChallenges.objects.filter(
                    courseID=current_course, hasStarted=False, hasEnded=False)
                context_dict['duel_current_filter'] = 'Completeness Status: Not Started Duels'
            elif type_id == 'expired':
                duel_challenges = []
                duel_challenges_raw = DuelChallenges.objects.filter(
                    courseID=current_course, hasStarted=True, hasEnded=True)
                for duel_challenge_raw in duel_challenges_raw:
                    if not Winners.objects.filter(DuelChallengeID=duel_challenge_raw):
                        duel_challenges.append(duel_challenge_raw)
                context_dict['duel_current_filter'] = 'Completeness Status: Expired Duels'
            elif type_id == 'in_progress':
                duel_challenges = DuelChallenges.objects.filter(
                    courseID=current_course, hasStarted=True, hasEnded=False)
                context_dict['duel_current_filter'] = 'Completeness Status: Duels in progress'
            else:
                duel_challenges = []
                duel_challenges_raw = DuelChallenges.objects.filter(
                    courseID=current_course, hasStarted=True, hasEnded=True)
                for duel_challenge_raw in duel_challenges_raw:
                    if Winners.objects.filter(DuelChallengeID=duel_challenge_raw):
                        duel_challenges.append(duel_challenge_raw)
                context_dict['duel_current_filter'] = 'Completeness Status: Completed Duels'

        elif filter_type == 'acceptance_status':
            if type_id == 'accepted':
                duel_challenges = DuelChallenges.objects.filter(
                    courseID=current_course, status=2)
                context_dict['duel_current_filter'] = 'Acceptance Status: Accepted Duels'
            else:
                duel_challenges = DuelChallenges.objects.filter(
                    courseID=current_course, status=1)
                context_dict['duel_current_filter'] = 'Acceptance Status: Pending Duels'
        else:
            duel_challenges = DuelChallenges.objects.filter(
                courseID=current_course)
            context_dict['duel_current_filter'] = 'All'

        duel_topic_ids = []
        duel_topic_names = []
        course_topics = CoursesTopics.objects.filter(courseID=current_course)
        for topic in course_topics:
            duel_topic_ids.append('topic---'+str(topic.topicID.topicID))
            duel_topic_names.append(topic.topicID.topicName)
        context_dict['duel_topics'] = zip(duel_topic_names, duel_topic_ids)

        reg_students = StudentRegisteredCourses.objects.filter(
            courseID=current_course)
        student_names = []
        student_ids = []
        for reg_student in reg_students:
            student_names.append(reg_student.studentID.user.last_name)
            student_ids.append(
                'student---'+reg_student.studentID.user.username)
        context_dict['duel_reg_students'] = zip(student_names, student_ids)

        duel_chall = []
        challenger_avatars = []
        challengee_avatars = []
        duel_topics = []
        has_expired_list = []
        for duel_challenge in duel_challenges:
            challengee_av = StudentRegisteredCourses.objects.get(
                studentID=duel_challenge.challengee, courseID=duel_challenge.courseID)
            challengee_avatars.append(challengee_av.avatarImage)
            challenger_av = StudentRegisteredCourses.objects.get(
                studentID=duel_challenge.challenger, courseID=duel_challenge.courseID)
            challenger_avatars.append(challenger_av.avatarImage)
            duel_chall.append(duel_challenge)
            # Get Topics
            chall_topics = ChallengesTopics.objects.filter(
                challengeID=duel_challenge.challengeID)
            topic_names = ""
            for chall_topic in chall_topics:
                topic_names += chall_topic.topicID.topicName + "   "
            duel_topics.append(topic_names)
            if duel_challenge.hasEnded:
                if not Winners.objects.filter(DuelChallengeID=duel_challenge):
                    has_expired_list.append(True)
                else:
                    has_expired_list.append(False)
            else:
                has_expired_list.append(False)

        return (zip(duel_chall, challenger_avatars, challengee_avatars, duel_topics, has_expired_list), context_dict)

    context_dict = {}
    if 'currentCourseID' in request.session:
        context_dict, current_course = initialContextDict(request)
        context_dict['current_course'] = current_course

        if request.POST:
            if 'duel_filter' in request.POST:
                type_id = request.POST['duel_filter'].split('---')
                if type_id[0] == 'topic':
                    context_dict['duel_challenges'], context_dict = get_duel_challenges_filter(
                        'topic', type_id[1], current_course, context_dict)
                elif type_id[0] == 'completeness_status':
                    context_dict['duel_challenges'], context_dict = get_duel_challenges_filter(
                        'completeness_status', type_id[1], current_course, context_dict)
                elif type_id[0] == 'acceptance_status':
                    context_dict['duel_challenges'], context_dict = get_duel_challenges_filter(
                        'acceptance_status', type_id[1], current_course, context_dict)
                elif type_id[0] == 'student':
                    context_dict['duel_challenges'], context_dict = get_duel_challenges_filter(
                        'student', type_id[1], current_course, context_dict)
                else:
                    context_dict['duel_challenges'], context_dict = get_duel_challenges_filter(
                        'all', 0, current_course, context_dict)

        else:
            context_dict['duel_challenges'], context_dict = get_duel_challenges_filter(
                'all', 0, current_course, context_dict)

    return render(request, 'Instructors/DuelReportForm.html', context_dict)


def duel_challenge_report(request):

    if 'currentCourseID' in request.session:
        context_dict = {}
        context_dict, current_course = initialContextDict(request)
        context_dict['current_course'] = current_course
        if 'duelChallengeID' in request.GET:

            duel_challenge = DuelChallenges.objects.get(
                courseID=current_course, duelChallengeID=int(request.GET['duelChallengeID']))
            challengee_av = StudentRegisteredCourses.objects.get(
                studentID=duel_challenge.challengee, courseID=duel_challenge.courseID)
            context_dict['challengee_av'] = challengee_av.avatarImage
            context_dict['challengee'] = duel_challenge.challengee.user.first_name + \
                "  " + duel_challenge.challengee.user.last_name
            challenger_av = StudentRegisteredCourses.objects.get(
                studentID=duel_challenge.challenger, courseID=duel_challenge.courseID)
            context_dict['challenger_av'] = challenger_av.avatarImage
            context_dict['challenger'] = duel_challenge.challenger.user.first_name + \
                "  " + duel_challenge.challenger.user.last_name
            context_dict['duel_challenge'] = duel_challenge

            if not duel_challenge.hasEnded and duel_challenge.hasStarted:
                context_dict['in_progress'] = True

            if duel_challenge.hasEnded:
                if not Winners.objects.filter(DuelChallengeID=duel_challenge):
                    context_dict['hasExpired'] = True
                else:
                    winners = Winners.objects.filter(
                        DuelChallengeID=duel_challenge, courseID=current_course)
                    if len(winners) == 2:
                        context_dict['winner1'] = winners[0].studentID.user.first_name + \
                            "  " + winners[0].studentID.user.last_name
                        context_dict['winner2'] = winners[1].studentID.user.first_name + \
                            "  " + winners[1].studentID.user.last_name
                        context_dict['w1'] = StudentChallenges.objects.filter(
                            studentID=winners[0].studentID, challengeID=duel_challenge.challengeID, courseID=current_course).earliest('startTimestamp')
                        context_dict['w2'] = StudentChallenges.objects.filter(
                            studentID=winners[1].studentID, challengeID=duel_challenge.challengeID, courseID=current_course).earliest('startTimestamp')
                    elif len(winners) == 1:
                        context_dict['winner'] = context_dict['winner1'] = winners[0].studentID.user.first_name + \
                            "  " + winners[0].studentID.user.last_name
                        context_dict['w'] = StudentChallenges.objects.filter(
                            studentID=winners[0].studentID, challengeID=duel_challenge.challengeID, courseID=current_course).earliest('startTimestamp')

            ccparams = CourseConfigParams.objects.get(courseID=current_course)
            context_dict['ccparams'] = ccparams

            context_dict['total_award'] = ccparams.vcDuelParticipants + \
                ccparams.vcDuel + 2 * duel_challenge.vcBet

            return render(request, 'Instructors/DuelChallengeReport.html', context_dict)

    return redirect('/oneUp/instructors/challengeClassmatesReport')
