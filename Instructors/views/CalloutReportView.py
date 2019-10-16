'''
Created on Oct 14, 2019

@author: omar
'''

from Students.models import CalloutParticipants, Callouts, CalloutStats, StudentRegisteredCourses, StudentChallenges, Student
from Instructors.models import ChallengesTopics, Topics, CoursesTopics
from django.shortcuts import render, redirect
from Instructors.views.utils import initialContextDict
from Badges.models import CourseConfigParams
from Instructors.views.utils import utcDate


def callout_report(request):

    def get_callout_filter(filter_type, type_id, current_course, context_dict):

        if filter_type == 'topic':
            callouts_raw = Callouts.objects.filter(
                courseID=current_course)
            callouts = []

            topics_raw = Topics.objects.filter(topicID=type_id)
            context_dict['callout_current_filter'] = 'Topic: ' + \
                topics_raw[0].topicName

            for callout_raw in callouts_raw:
                chall_topics = ChallengesTopics.objects.filter(
                    topicID__topicID=type_id, challengeID=callout_raw.challengeID)
                if chall_topics:
                    callouts.append(callout_raw)

        elif filter_type == 'student':
            callouts_sender = Callouts.objects.filter(
                courseID=current_course, sender__user__username=type_id)
            callouts_participant_raw = CalloutParticipants.objects.filter(
                courseID=current_course, participantID__user__username=type_id)
            callouts_participant = [
                callout_participant_raw.calloutID for callout_participant_raw in callouts_participant_raw]
            callouts = list(callouts_sender) + \
                list(callouts_participant)
            student = Student.objects.get(user__username=type_id)
            context_dict['callout_current_filter'] = 'Student: ' + \
                student.user.last_name

        elif filter_type == 'completeness_status':
            if type_id == 'in_progress':
                callouts = Callouts.objects.filter(
                    courseID=current_course, hasEnded=False)
                context_dict['callout_current_filter'] = 'Completeness Status: Callouts In Progress'
            else:
                callouts = Callouts.objects.filter(
                    courseID=current_course, hasEnded=True)
                context_dict['callout_current_filter'] = 'Completeness Status: Ended Callouts'

        elif filter_type == 'callout_type':
            if type_id == 'individual':
                callouts = Callouts.objects.filter(
                    courseID=current_course, isIndividual=True)
                context_dict['callout_current_filter'] = 'Callout Type: Individual Callouts'
            else:
                callouts = Callouts.objects.filter(
                    courseID=current_course, isIndividual=False)
                context_dict['callout_current_filter'] = 'Callout Type: Class Callouts'
        else:
            callouts = Callouts.objects.filter(
                courseID=current_course)
            context_dict['callout_current_filter'] = 'All'

        callout_topic_ids = []
        callout_topic_names = []
        course_topics = CoursesTopics.objects.filter(courseID=current_course)
        for topic in course_topics:
            callout_topic_ids.append('topic---'+str(topic.topicID.topicID))
            callout_topic_names.append(topic.topicID.topicName)
        context_dict['callout_topics'] = zip(
            callout_topic_names, callout_topic_ids)

        reg_students = StudentRegisteredCourses.objects.filter(
            courseID=current_course)
        student_names = []
        student_ids = []
        for reg_student in reg_students:
            student_names.append(reg_student.studentID.user.last_name)
            student_ids.append(
                'student---'+reg_student.studentID.user.username)
        context_dict['callout_reg_students'] = zip(student_names, student_ids)

        callout_chall = []
        sender_avatars = []
        participant_avatars = []
        callout_topics = []
        has_expired_list = []
        for callout in callouts:
            sender_av = StudentRegisteredCourses.objects.get(
                studentID=callout.sender, courseID=callout.courseID)
            sender_avatars.append(sender_av.avatarImage)
            if callout.isIndividual:
                callout_participant = CalloutParticipants.objects.get(
                    calloutID=callout)
                participant_av = StudentRegisteredCourses.objects.get(
                    studentID=callout_participant.participantID, courseID=callout.courseID)
                participant_avatars.append(
                    [True, participant_av.avatarImage, callout_participant.participantID.user.last_name])
            else:
                participant_avatars.append([False, "", ""])
            callout_chall.append(callout)
            # Get Topics
            chall_topics = ChallengesTopics.objects.filter(
                challengeID=callout.challengeID)
            topic_names = ""
            for chall_topic in chall_topics:
                topic_names += chall_topic.topicID.topicName + "   "
            callout_topics.append(topic_names)

            if callout.hasEnded:
                has_expired_list.append(True)
            else:
                has_expired_list.append(False)

        return (zip(callout_chall, sender_avatars, participant_avatars, callout_topics, has_expired_list), context_dict)

    context_dict = {}
    if 'currentCourseID' in request.session:
        context_dict, current_course = initialContextDict(request)
        context_dict['current_course'] = current_course

        if request.POST:
            if 'callout_filter' in request.POST:
                type_id = request.POST['callout_filter'].split('---')
                if type_id[0] == 'topic':
                    context_dict['callouts'], context_dict = get_callout_filter(
                        'topic', type_id[1], current_course, context_dict)
                elif type_id[0] == 'completeness_status':
                    context_dict['callouts'], context_dict = get_callout_filter(
                        'completeness_status', type_id[1], current_course, context_dict)
                elif type_id[0] == 'callout_type':
                    context_dict['callouts'], context_dict = get_callout_filter(
                        'callout_type', type_id[1], current_course, context_dict)
                elif type_id[0] == 'student':
                    context_dict['callouts'], context_dict = get_callout_filter(
                        'student', type_id[1], current_course, context_dict)
                else:
                    context_dict['callouts'], context_dict = get_callout_filter(
                        'all', 0, current_course, context_dict)

        else:
            context_dict['callouts'], context_dict = get_callout_filter(
                'all', 0, current_course, context_dict)

    return render(request, 'Instructors/CalloutReportForm.html', context_dict)


def callout_challenge_report(request):

    if 'currentCourseID' in request.session:
        context_dict = {}
        context_dict, current_course = initialContextDict(request)
        context_dict['current_course'] = current_course
        if 'calloutID' in request.GET:
            call_out = Callouts.objects.get(
                calloutID=int(request.GET['calloutID']))
            context_dict["callout"] = call_out

            context_dict["sender"] = call_out.sender.user.last_name

            sender_av = StudentRegisteredCourses.objects.get(
                studentID=call_out.sender, courseID=call_out.courseID)
            context_dict["sender_av"] = sender_av.avatarImage

            sender_call_out_stat = CalloutStats.objects.get(
                studentID=call_out.sender, calloutID=call_out, courseID=current_course)
            sender_score = sender_call_out_stat.studentChallenge.testScore
            context_dict['sender_score'] = sender_score
            context_dict['test_score'] = sender_call_out_stat.studentChallenge.challengeID.totalScore

            if call_out.isIndividual:
                call_out_part = CalloutParticipants.objects.get(
                    calloutID=call_out)
                context_dict["participant"] = call_out_part.participantID.user.last_name

                participant_av = StudentRegisteredCourses.objects.get(
                    studentID=call_out_part.participantID, courseID=call_out.courseID)
                context_dict["participant_av"] = participant_av.avatarImage

            call_out_participant_objects = CalloutParticipants.objects.filter(
                calloutID=call_out, courseID=current_course).order_by('?')

            participant_avatars = []
            participant_last_names = []
            call_out_participants = []
            submit_times = []
            participant_scores = []
            submission_status = []
            winning_status = []

            for call_out_participant in call_out_participant_objects:
                participant_avatars.append(StudentRegisteredCourses.objects.get(
                    studentID=call_out_participant.participantID, courseID=current_course).avatarImage)
                call_out_participants.append(call_out_participant)

                participant_last_names.append(
                    call_out_participant.participantID.user.last_name)

                if call_out_participant.hasWon:
                    winning_status.append("Won")
                elif call_out.hasEnded:
                    winning_status.append("Failed")
                else:
                    winning_status.append("-")

                try:
                    participant_call_out_stat = CalloutStats.objects.get(
                        studentID=call_out_participant.participantID, studentChallenge__challengeID=call_out.challengeID, calloutID=call_out, courseID=current_course)
                    participant_scores.append(
                        participant_call_out_stat.studentChallenge.testScore)
                    submit_times.append(
                        participant_call_out_stat.submitTime)
                    submission_status.append(True)

                except:
                    participant_scores.append("-")
                    submit_times.append("-")
                    if call_out_participant.hasSubmitted:
                        submission_status.append(True)
                    else:
                        submission_status.append(False)

            context_dict['call_outs'] = zip(
                participant_avatars, participant_last_names, call_out_participants, submit_times, participant_scores, submission_status, winning_status)
            return render(request, 'Instructors/CalloutChallengeReport.html', context_dict)

    return redirect('/oneUp/instructors/CalloutReport')
