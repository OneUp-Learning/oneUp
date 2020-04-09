'''
Created on Apr 2, 2019
@author: omar
'''
from django.shortcuts import render, redirect
from django.utils import timezone
from Students.views.utils import studentInitialContextDict
from Badges.models import CourseConfigParams, BadgesVCLog
from Students.models import StudentRegisteredCourses, Callouts, StudentChallenges, CalloutParticipants, StudentConfigParams, StudentVirtualCurrency, CalloutStats, DuelChallenges, Student
from Instructors.models import CoursesTopics, Topics, Challenges, ChallengesTopics, Courses, ChallengesQuestions
from Instructors.views.whoAddedVCAndBadgeView import create_badge_vc_log_json
from notify.signals import notify
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from celery import Celery
import json
from Instructors.views.courseInfoView import courseInformation
from django.http import JsonResponse

from Badges.enums import Event
from Badges.events import register_event_simple

app = Celery('Students', broker='amqp://localhost')
app.config_from_object('django.conf:settings', namespace='CELERY')


@app.task
def end_call_out(call_out_id, course_id):
    ''' This function ends a call out if it has not ended yet'''
    try:
        course = Courses.objects.get(courseID=course_id)
        call_out = Callouts.objects.get(calloutID=call_out_id, courseID=course)
        call_out.hasEnded = True
        call_out.save()
    except:
        print("error")


def evaluator(call_out, sender_stat, call_out_participant, participant_id, current_course, participant_chall, already_taken=False):
    '''This function evaluates a call out manually, in class call out case, this function
       evaluates the highest already taken challenge score against the sender's score 
       if warm up challenge has already been taken by participant '''

    # if call out has ended, then abord
    if call_out.hasEnded:
        return

    def reward_sender(sender_stat, current_course, call_out):
        '''Reward Sender when participant participates'''

        if sender_stat.calloutVC > 0:
            vc_winner = StudentRegisteredCourses.objects.get(
                studentID=call_out.sender, courseID=current_course)
            # sender gets the callout participation amount of virtual currency set by teacher
            virtualCurrencyAmount = vc_winner.virtualCurrencyAmount + sender_stat.calloutVC
            vc_winner.virtualCurrencyAmount = virtualCurrencyAmount
            vc_winner.save()

            # save earning transaction
            w_student_vc = StudentVirtualCurrency()
            w_student_vc.courseID = current_course
            w_student_vc.studentID = call_out.sender
            w_student_vc.objectID = 0
            w_student_vc.value = sender_stat.calloutVC
            w_student_vc.vcName = "Callout "+call_out.challengeID.challengeName
            w_student_vc.vcDescription = "Virtual currency for sending the individual call out, " + \
                call_out.challengeID.challengeName
            w_student_vc.save()

            # Record this trasaction in the log to show that the system awarded this vc
            studentAddBadgeLog = BadgesVCLog()
            studentAddBadgeLog.courseID = current_course
            log_data = create_badge_vc_log_json("System", w_student_vc, "VC", "Callout")
            studentAddBadgeLog.log_data = json.dumps(log_data)
            studentAddBadgeLog.save()

            # Notify sender about the call out
            notify.send(None, recipient=call_out.sender.user, actor=call_out.sender.user,
                        verb="You have won the call out "+call_out.challengeID.challengeName, nf_type='callout won', extra=json.dumps({"course": str(current_course), "name": str(current_course.courseName), "related_link": '/oneUp/students/CalloutDescription?call_out_participant_id='+str(call_out_participant.id)+'&participant_id='+str(call_out_participant.participantID.user.id)}))

            # mini req for calloutSent event
            mini_req = {
                'currentCourseID': current_course.pk,
                'user': call_out.sender.user.username,
            }
            # register event
            register_event_simple(Event.virtualCurrencyEarned, mini_req, objectId=sender_stat.calloutVC)

    # If the warmup challenge has been taken by participant
    # check if participant has performed the same or better
    # if yes, then reward participant and terminate participation,
    # if not, then give participant a chance to retake the warmup challenge

    if already_taken:
        participant_score = participant_chall.testScore

        if participant_score >= sender_stat.studentChallenge.testScore:

            # Add neccessary fields for callout stats
            call_out_stat = CalloutStats()
            call_out_stat.calloutID = call_out
            call_out_stat.courseID = current_course
            call_out_stat.calloutVC = sender_stat.calloutVC
            call_out_stat.studentID = participant_id
            call_out_stat.studentChallenge = participant_chall
            call_out_stat.submitTime = participant_chall.endTimestamp

            # Save Calloutstats object
            call_out_stat.save()

            call_out_participant.hasSubmitted = True
            call_out_participant.hasWon = True
            call_out_participant.save()

            # Reward participant
            if sender_stat.calloutVC > 0:
                vc_winner = StudentRegisteredCourses.objects.get(
                    studentID=participant_id, courseID=current_course)
                # participant gets the call out participation award amount of virtual currency set by teacher
                virtualCurrencyAmount = vc_winner.virtualCurrencyAmount + sender_stat.calloutVC
                vc_winner.virtualCurrencyAmount = virtualCurrencyAmount
                vc_winner.save()

                # save earning transaction
                w_student_vc = StudentVirtualCurrency()
                w_student_vc.courseID = current_course
                w_student_vc.studentID = participant_id
                w_student_vc.objectID = 0
                w_student_vc.value = sender_stat.calloutVC
                w_student_vc.vcName = "Callout "+call_out.challengeID.challengeName
                w_student_vc.vcDescription = "You have perfomed the same as or better than the sender in the call out, " + \
                    call_out.challengeID.challengeName
                w_student_vc.save()

                # Record this trasaction in the log to show that the system awarded this vc
                studentAddBadgeLog = BadgesVCLog()
                studentAddBadgeLog.courseID = current_course
                log_data = create_badge_vc_log_json("System", w_student_vc, "VC", "Callout")
                studentAddBadgeLog.log_data = json.dumps(log_data)
                studentAddBadgeLog.save()

            # Check if any participant has participated in the class call out
            if not call_out.isIndividual:
                stats = CalloutStats.objects.filter(calloutID=call_out, courseID=current_course)
                # only reward sender once when there is only one participant and the sender the callout stats table
                if len(stats) == 2:
                    reward_sender(sender_stat, current_course, call_out)

            # Notify participant about the call out
            notify.send(None, recipient=participant_id.user, actor=participant_id.user,
                        verb="You have won the call out "+call_out.challengeID.challengeName, nf_type='callout won', extra=json.dumps({"course": str(current_course), "name": str(current_course.courseName), "related_link": '/oneUp/students/CalloutDescription?call_out_participant_id='+str(call_out_participant.id)+'&participant_id='+str(call_out_participant.participantID.user.id)}))

            # mini req for calloutSent event
            mini_req = {
                'currentCourseID': current_course.pk,
                'user': participant_id.user.username,
            }
            # register event
            if sender_stat.calloutVC > 0:
                register_event_simple(Event.virtualCurrencyEarned, mini_req, objectId=sender_stat.calloutVC)

            register_event_simple(Event.calloutWon, mini_req,
                                  objectId=call_out_stat.calloutID.calloutID)

    else:

        participant_score = participant_chall.testScore

        # Add neccessary fields for callout stats
        call_out_stat = CalloutStats()
        call_out_stat.calloutID = call_out
        call_out_stat.courseID = current_course
        call_out_stat.calloutVC = sender_stat.calloutVC
        call_out_stat.studentID = participant_id
        call_out_stat.studentChallenge = participant_chall

        # Save Calloutstats object
        call_out_stat.save()

        call_out_participant.hasSubmitted = True

        if call_out.isIndividual:

            # Reward Sender when participant participates
            reward_sender(sender_stat, current_course, call_out)

            call_out.hasEnded = True
            call_out.save()

        if participant_score >= sender_stat.studentChallenge.testScore:

            call_out_participant.hasWon = True
            call_out_participant.hasSubmitted = True
            call_out_participant.save()

            # Reward participant
            if sender_stat.calloutVC > 0:
                vc_winner = StudentRegisteredCourses.objects.get(
                    studentID=participant_id, courseID=current_course)
                # participant gets the call out participation award amount of virtual currency set by teacher
                virtualCurrencyAmount = vc_winner.virtualCurrencyAmount + sender_stat.calloutVC
                vc_winner.virtualCurrencyAmount = virtualCurrencyAmount
                vc_winner.save()

                # save earning transaction
                w_student_vc = StudentVirtualCurrency()
                w_student_vc.courseID = current_course
                w_student_vc.studentID = participant_id
                w_student_vc.objectID = 0
                w_student_vc.value = sender_stat.calloutVC
                w_student_vc.vcName = "Callout "+call_out.challengeID.challengeName
                w_student_vc.vcDescription = "You have perfomed the same as or better than the sender in the call out, " + \
                    call_out.challengeID.challengeName
                w_student_vc.save()

                # Record this trasaction in the log to show that the system awarded this vc
                studentAddBadgeLog = BadgesVCLog()
                studentAddBadgeLog.courseID = current_course
                log_data = create_badge_vc_log_json("System", w_student_vc, "VC", "Callout")
                studentAddBadgeLog.log_data = json.dumps(log_data)
                studentAddBadgeLog.save()

            # Check if any participant has participated in the class call out
            if not call_out.isIndividual:
                stats = CalloutStats.objects.filter(calloutID=call_out, courseID=current_course)
                # only reward sender once when there is only one participant and the sender the callout stats table
                if len(stats) == 2:
                    reward_sender(sender_stat, current_course, call_out)

            # Notify participant about the call out
            notify.send(None, recipient=participant_id.user, actor=participant_id.user,
                        verb="You have won the call out "+call_out.challengeID.challengeName, nf_type='callout won', extra=json.dumps({"course": str(current_course), "name": str(current_course.courseName), "related_link": '/oneUp/students/CalloutDescription?call_out_participant_id='+str(call_out_participant.id)+'&participant_id='+str(call_out_participant.participantID.user.id)}))

            # mini req for calloutSent event
            mini_req = {
                'currentCourseID': current_course.pk,
                'user': participant_id.user.username,
            }
            # register event
            if sender_stat.calloutVC > 0:
                register_event_simple(Event.virtualCurrencyEarned, mini_req, objectId=sender_stat.calloutVC)
                
            register_event_simple(Event.calloutWon, mini_req,
                                  objectId=call_out_stat.calloutID.calloutID)
        else:
            call_out_participant.hasWon = False
            call_out_participant.hasSubmitted = True
            call_out_participant.save()

            # Notify participant about the call out
            notify.send(None, recipient=participant_id.user, actor=participant_id.user,
                        verb="You have loast the call out "+call_out.challengeID.challengeName, nf_type='callout lost', extra=json.dumps({"course": str(current_course), "name": str(current_course.courseName), "related_link": '/oneUp/students/CalloutDescription?call_out_participant_id='+str(call_out_participant.id)+'&participant_id='+str(call_out_participant.participantID.user.id)}))

            # mini req for calloutSent event
            mini_req = {
                'currentCourseID': current_course.pk,
                'user': participant_id.user.username,
            }
            # register event
            register_event_simple(Event.calloutLost, mini_req,
                                  objectId=call_out_stat.calloutID.calloutID)

def get_sender_duel_challs(student_id,  current_course):
    '''get the challenger's and challengee's duel warm up challenges'''

    challenger_duels_as_challenger = DuelChallenges.objects.filter(challenger = student_id, courseID=current_course)
    challenger_duels_as_challengee = DuelChallenges.objects.filter(challengee = student_id, courseID=current_course)


    if not challenger_duels_as_challenger and not challenger_duels_as_challengee:
        return []
    challenger_duels = list(challenger_duels_as_challenger) + list(challenger_duels_as_challengee)
    challenger_duels_challs = []
    for challenger_duel in challenger_duels:
        challenger_duels_challs.append(challenger_duel.challengeID)
         
    return challenger_duels_challs

def get_challenger_challengee_duel_challs(student_id, challengee_id, current_course):
    '''get the challenger's and challengee's duel warm up challenges'''

    challenger_duels_as_challenger = DuelChallenges.objects.filter(challenger = student_id, courseID=current_course)
    challenger_duels_as_challengee = DuelChallenges.objects.filter(challengee = student_id, courseID=current_course)

    challengee_duels_as_challenger = DuelChallenges.objects.filter(challenger=challengee_id, courseID=current_course)
    challengee_duels_as_challengee = DuelChallenges.objects.filter(challengee=challengee_id, courseID=current_course)

    if not challenger_duels_as_challenger and not challenger_duels_as_challengee and not challengee_duels_as_challenger and not challengee_duels_as_challengee:
        return ([],[])
    challenger_duels = list(challenger_duels_as_challenger) + list(challenger_duels_as_challengee)
    challenger_duels_challs = []
    for challenger_duel in challenger_duels:
        if not challenger_duel.hasExpired:
            challenger_duels_challs.append(challenger_duel.challengeID)
         
    
    challengee_duels = list(challengee_duels_as_challenger) + list(challengee_duels_as_challengee)
    challengee_duels_challs = []
    for challengee_duel in challengee_duels:
        if not challenger_duel.hasExpired:
            challengee_duels_challs.append(challengee_duel.challengeID)
    
    return (challenger_duels_challs, challengee_duels_challs)

@login_required
def callout_create(request):
    ''' Create call out when the request it is POST and Prep data for call out creation if request it is POST '''
    context_dict, current_course = studentInitialContextDict(request)
    student_id = context_dict['student']

    # if request is POST, create call out
    if request.POST:

        # Create a new callout object
        callout = Callouts()

        #
        # Add necessary fields to callout
        #

        callout.courseID = current_course
        callout.sender = student_id
        # Get utc time
        time = timezone.now() # TODO: Use current localtime
        # send time is when the callout is being created
        callout.sendTime = time
        # end time is send time plus a week. Basically the callout expires afte a week
        callout.endTime = time + timedelta(weeks=1)

        # Retrieve challenge id from request
        challenge_id = request.POST['challenge_id']
        # Get challenge and add it to callout
        challenge = Challenges.objects.get(
            courseID=current_course, challengeID=challenge_id)
        callout.challengeID = challenge

        # Retrive callout and determine if it is individual
        callout_type = request.POST['callout_type']
        if callout_type == 'individual':
            callout.isIndividual = True
        else:
            callout.isIndividual = False

        # save object
        callout.save()

        # Get course config params
        ccparm = CourseConfigParams.objects.get(courseID=current_course)

        # Add neccessary fields for callout stats
        call_out_stat = CalloutStats()
        call_out_stat.calloutID = callout
        call_out_stat.courseID = current_course
        call_out_stat.calloutVC = ccparm.vcCallout
        call_out_stat.studentID = student_id
        call_out_stat.studentChallenge = StudentChallenges.objects.filter(
            challengeID=challenge, courseID=current_course, studentID=student_id, challengeID__isGraded=False).latest('testScore')

        # Save Calloutstats object
        call_out_stat.save()
        print()
        print("Saved Call Out")
        print()

        # mini req for calloutSent event
        mini_req = {
            'currentCourseID': current_course.pk,
            'user': student_id.user.username,
        }
        # register event
        register_event_simple(Event.calloutSent, mini_req,
                              objectId=call_out_stat.calloutID.calloutID)

        # if the callout is individual then retrieve particapant id from request, get participant object and save it to CalloutParticipants table
        if callout.isIndividual:
            id_av = request.POST['participant_id'].split("---")
            participant_reg_crs = StudentRegisteredCourses.objects.get(
                studentID__user__id=int(id_av[0]), courseID=current_course)
            participant_stud = participant_reg_crs.studentID
            print("participant")
            print(participant_stud)

            # Add necessary fields
            participant = CalloutParticipants()
            participant.calloutID = callout
            participant.courseID = current_course
            participant.participantID = participant_stud

            # Save CalloutParticipants object
            participant.save()

            # Save Calloutstats object
            call_out_stat.save()

            # Notify participant about the call out
            notify.send(None, recipient=participant_stud.user, actor=participant_stud.user,
                        verb="You have recieved an individual call out", nf_type='individual callout invitation', extra=json.dumps({"course": str(current_course), "name": str(current_course.courseName), "related_link": '/oneUp/students/CalloutDescription?call_out_participant_id='+str(participant.id)+'&participant_id='+str(participant.participantID.user.id)}))

            # mini req for calloutSent event
            mini_req = {
                'currentCourseID': current_course.pk,
                'user': participant_stud.user.username
            }
            # register event
            register_event_simple(Event.calloutRequested, mini_req,
                                  objectId=call_out_stat.calloutID.calloutID)

        # if it is class callout, get all participants and create CalloutParticipants object for it
        else:
            reg_students = StudentRegisteredCourses.objects.filter(courseID=current_course).exclude(
                studentID=student_id).exclude(studentID__isTestStudent=True)
            for participant_stud in reg_students:
                # try to get particpant's StudentConfigParams object
                # if it does not exist then catch it
                try:
                    scparam = StudentConfigParams.objects.get(
                        studentID=participant_stud.studentID, courseID=current_course)
                    # check if it is student wants to participate
                    if scparam.participateInCallout:
                        # Add necessary fields
                        participant = CalloutParticipants()
                        participant.calloutID = callout
                        participant.courseID = current_course
                        participant.participantID = participant_stud.studentID
                        # Save object
                        participant.save()

                        # Save Calloutstats object
                        call_out_stat.save()

                        # Notify participant about the call out
                        notify.send(None, recipient=participant_stud.studentID.user, actor=participant_stud.studentID.user,
                                    verb="You have recieved a class call out", nf_type='class callout invitation', extra=json.dumps({"course": str(current_course), "name": str(current_course.courseName), "related_link": '/oneUp/students/CalloutDescription?call_out_participant_id='+str(participant.id)+'&participant_id='+str(participant.participantID.user.id)}))

                        # for event
                        mini_req = {
                            'currentCourseID': current_course.pk,
                            'user': participant_stud.studentID.user.username,
                        }
                        # register event
                        register_event_simple(Event.calloutRequested, mini_req,
                                              objectId=call_out_stat.calloutID.calloutID)

                        if StudentChallenges.objects.filter(studentID=participant_stud.studentID, courseID=current_course, challengeID=callout.challengeID, challengeID__isGraded=False):

                            participant_chall = StudentChallenges.objects.filter(
                                challengeID=callout.challengeID, studentID=participant_stud.studentID, courseID=current_course, challengeID__isGraded=False).latest('testScore')
                            evaluator(callout, call_out_stat, participant, participant_stud.studentID,
                                      current_course, participant_chall, already_taken=True)

                except:
                    # Add necessary fields
                    participant = CalloutParticipants()
                    participant.calloutID = callout
                    participant.courseID = current_course
                    participant.participantID = participant_stud.studentID

                    # Save object
                    participant.save()

                    # Notify participant about the call out
                    notify.send(None, recipient=participant_stud.studentID.user, actor=participant_stud.studentID.user,
                                verb="You have recieved a class call out", nf_type='class callout invitation', extra=json.dumps({"course": str(current_course), "name": str(current_course.courseName), "related_link": '/oneUp/students/CalloutDescription?call_out_participant_id='+str(participant.id)+'&participant_id='+str(participant.participantID.user.id)}))

                    # for event
                    mini_req = {
                        'currentCourseID': current_course.pk,
                        'user': participant_stud.studentID.user.username,
                    }
                    # register event
                    register_event_simple(Event.calloutRequested, mini_req,
                                          objectId=call_out_stat.calloutID.calloutID)

                    if StudentChallenges.objects.filter(studentID=participant_stud.studentID, courseID=current_course, challengeID=callout.challengeID, challengeID__isGraded=False):
                        participant_chall = StudentChallenges.objects.filter(
                            challengeID=callout.challengeID, studentID=participant_stud.studentID, courseID=current_course, challengeID__isGraded=False).latest('testScore')
                        evaluator(callout, call_out_stat, participant, participant_stud.studentID,
                                  current_course, participant_chall, already_taken=True)

        ################################################################################################################################################
        # End call out after specified time using celery
        # get database end time and add 5 seconds from it to be consistent with network latency
        end_time = callout.endTime + timedelta(seconds=3)
        end_call_out.apply_async(
            (callout.calloutID, current_course.courseID), eta=end_time)
        ##################################################################################################################################################

        return redirect('/oneUp/students/Callouts')

    if "direct_warmup_callout" in request.GET:
        context_dict["direct_warmup_callout"] = True

    # get list of participants randomly and exclude the sender and test students
    reg_students = StudentRegisteredCourses.objects.filter(courseID=current_course).exclude(
        studentID=student_id).exclude(studentID__isTestStudent=True).order_by('?')

    # if no student to participate, cancel creation and redirect to No callout Form
    if not reg_students:
        return render(request, 'Students/NoCalloutForm.html', context_dict)

    # Get avatars and participants
    avatars = []
    participants = []
    ids_avs = []
    for participant in reg_students:
        # try to get particpant's StudentConfigParams object
        # if it does not exist then catch it
        try:
            scparam = StudentConfigParams.objects.get(
                studentID=participant.studentID, courseID=current_course)
            # check if it is student wants to participate
            if scparam.participateInCallout:
                participants.append(participant)
                avatar = participant.avatarImage
                avatars.append(avatar)
                # concatinate student id and avatar and add '---' as a delimeter to be used for the frontend to facilate the selection of avatar
                ids_avs.append(
                    str(participant.studentID.user.id)+"---"+str(avatar))
        except:
            participants.append(participant)
            avatar = participant.avatarImage
            avatars.append(avatar)
            # concatinate student id and avatar and add '---' as a delimeter to be used for the frontend to facilate the selection of avatar
            ids_avs.append(str(participant.studentID.user.id) +
                           "---"+str(avatar))

    # get the first avatar to be displayed as first option in the dropdown interface
    if avatars:
        context_dict['first_avatar'] = avatars[0]
    context_dict['participants_range'] = zip(
        range(0, len(avatars)), avatars, participants, ids_avs)

    s_challenges = StudentChallenges.objects.filter(
        courseID=current_course, studentID=student_id, challengeID__isGraded=False)

    # Get unique warmp challenges that are completed and are equal or greater than 30% by sender
    sender_challenges = []
    seen_challenges = set()
    for s_c in s_challenges[::-1]:
        if not s_c.challengeID in seen_challenges:
            s_chall = StudentChallenges.objects.filter(
                courseID=current_course, studentID=student_id, challengeID=s_c.challengeID, challengeID__isGraded=False).latest('testScore')
            if float(s_chall.challengeID.totalScore) > 0.0:
                percentage = (float(s_chall.testScore) /
                              float(s_chall.challengeID.totalScore)) * 100
            else:
                percentage = 0.0
            # if the sender test score for this challenge is greater than 30% then consider the challenge
            if percentage > 30.0:
                sender_challenges.append(s_chall)
        seen_challenges.add(s_c.challengeID)

    participant_challenges = StudentChallenges.objects.filter(
        courseID=current_course, studentID=participants[0].studentID, challengeID__isGraded=False)

    # get participant's warmup challenges ids from the challenges table
    taken_participant_challenges = [
        challenge.challengeID for challenge in participant_challenges if not challenge.challengeID.isGraded]

    # get all participant's call_outs' challenges
    participant_call_outs = CalloutParticipants.objects.filter(
        participantID=participants[0].studentID, courseID=current_course)
    participant_call_outs_challenges = [
        call_out.calloutID.challengeID for call_out in participant_call_outs]

    # get all sender's call_outs' challenges
    sender_call_outs = Callouts.objects.filter(
        sender=student_id, courseID=current_course)
    sender_call_outs_challenges = [
        call_out.challengeID for call_out in sender_call_outs]

    challenger_duels_challs, challengee_duels_challs = get_challenger_challengee_duel_challs(student_id, participants[0].studentID, current_course)


    qualified_challenges = []

    for sender_challenge in sender_challenges:
        if not sender_challenge.challengeID.isGraded and not sender_challenge.challengeID in taken_participant_challenges and not sender_challenge.challengeID in participant_call_outs_challenges and not sender_challenge.challengeID in challenger_duels_challs and not sender_challenge.challengeID in challengee_duels_challs and not sender_challenge.challengeID in sender_call_outs_challenges:
            qualified_challenges.append(sender_challenge)

    context_dict['challenges'] = qualified_challenges

    return render(request, 'Students/CalloutCreateForm.html', context_dict)


@login_required
def get_class_callout_qualified_challenges(request):
    ''' When sender wants to call out the whole class, this function is called and returns all sender's taken warmup challenges'''

    c_d, current_course = studentInitialContextDict(request)
    student_id = c_d['student']
    context_dict = {}

    # get all sender warmup taken challenges
    # store challenges ids and names as strings with '---' as a delimeter to get around jason serialization
    ids_names_taken_challenges = []
    s_challenges = StudentChallenges.objects.filter(
        courseID=current_course, studentID=student_id, challengeID__isGraded=False)

    # Get unique warmp challenges that are completed and are equal or greater than 30% by sender
    sender_challenges = []
    seen_challenges = set()
    for s_c in s_challenges[::-1]:
        if not s_c.challengeID in seen_challenges:
            s_chall = StudentChallenges.objects.filter(
                courseID=current_course, studentID=student_id, challengeID=s_c.challengeID, challengeID__isGraded=False).latest('testScore')
            if float(s_chall.challengeID.totalScore) > 0.0:
                percentage = (float(s_chall.testScore) /
                              float(s_chall.challengeID.totalScore)) * 100
            else:
                percentage = 0.0
            # if the sender test score for this challenge is greater than 30% then consider the challenge
            if percentage > 30.0:
                sender_challenges.append(s_chall)
        seen_challenges.add(s_c.challengeID)

    # get all sender's call_outs' challenges
    sender_call_outs = Callouts.objects.filter(
        sender=student_id, courseID=current_course)
    sender_call_outs_challenges = [
        call_out.challengeID for call_out in sender_call_outs]

    sender_call_outs_parts = CalloutParticipants.objects.filter(
        participantID=student_id, courseID=current_course)
    for sender_call_outs_part in sender_call_outs_parts:
        sender_call_outs_challenges.append(
            sender_call_outs_part.calloutID.challengeID)

    sender_duel_challenges = get_sender_duel_challs(student_id, current_course)

    for challenge in sender_challenges:
        if not challenge.challengeID in sender_call_outs_challenges and not challenge.challengeID in sender_duel_challenges:
            ids_names_taken_challenges.append(str(
                challenge.challengeID.challengeID)+"---"+challenge.challengeID.challengeName)

    context_dict["challenges"] = ids_names_taken_challenges

    return JsonResponse(context_dict)


@login_required
def get_individual_callout_qualified_challenges(request):
    ''' When sender wants to call out an individual, this function is called and returns all sender taken warmup challenges excluding all the warmup challenges taken by participant'''

    c_d, current_course = studentInitialContextDict(request)
    student_id = c_d['student']
    context_dict = {}

    # get all sender warmup taken challenges excluding participants' taken warmup challenges
    # store challenges ids and names as strings with '---' as a delimeter to get around jason serialization
    ids_names_challenges = []

    s_challenges = StudentChallenges.objects.filter(
        courseID=current_course, studentID=student_id, challengeID__isGraded=False)

    # Get unique warmp challenges that are completed and are equal or greater than 30% by sender
    sender_challenges = []
    seen_challenges = set()
    for s_c in s_challenges[::-1]:
        if not s_c.challengeID in seen_challenges:
            s_chall = StudentChallenges.objects.filter(
                courseID=current_course, studentID=student_id, challengeID=s_c.challengeID, challengeID__isGraded=False).latest('testScore')
            if float(s_chall.challengeID.totalScore) > 0.0:
                percentage = (float(s_chall.testScore) /
                              float(s_chall.challengeID.totalScore)) * 100
            else:
                percentage = 0.0
            # if the sender test score for this challenge is greater than 30% then consider the challenge
            if percentage > 30.0:
                sender_challenges.append(s_chall)
        seen_challenges.add(s_c.challengeID)

    participant_id = request.GET['participant_id']
    participant_challenges = StudentChallenges.objects.filter(
        courseID=current_course, studentID__user__id=participant_id, challengeID__isGraded=False)

    # get participants warmup challenges ids from the challenges table
    taken_participant_challenges = [
        challenge.challengeID for challenge in participant_challenges if not challenge.challengeID.isGraded]

    # get all participant's call_outs' challenges
    participant_call_outs1 = CalloutParticipants.objects.filter(
        participantID__user__id=participant_id, courseID=current_course)
    participant_call_outs_challenges1 = [
        call_out.calloutID.challengeID for call_out in participant_call_outs1]
    participant_call_outs2 = Callouts.objects.filter(sender__user__id=participant_id, courseID=current_course)
    participant_call_outs_challenges2 = [
        call_out.challengeID for call_out in participant_call_outs2]

    participant_call_outs_challenges = participant_call_outs_challenges1 + participant_call_outs_challenges2

    participant = Student.objects.get(user__id=participant_id)
    challenger_duels_challs, challengee_duels_challs = get_challenger_challengee_duel_challs(student_id, participant, current_course)


    # get all sender's call_outs' challenges
    sender_call_outs1 = Callouts.objects.filter(
        sender=student_id, courseID=current_course)
    sender_call_outs2 = CalloutParticipants.objects.filter(participantID=student_id, courseID=current_course)

    sender_call_outs_challenges1 = [
        call_out.challengeID for call_out in sender_call_outs1]
    sender_call_outs_challenges2 = [
        participant_callout.calloutID.challengeID for participant_callout in sender_call_outs2]
    sender_call_outs_challenges = sender_call_outs_challenges1 + sender_call_outs_challenges2

    for sender_challenge in sender_challenges:
        if not sender_challenge.challengeID.isGraded and not sender_challenge.challengeID in taken_participant_challenges and not sender_challenge.challengeID in participant_call_outs_challenges and not sender_challenge.challengeID in challenger_duels_challs and not sender_challenge.challengeID in challengee_duels_challs and not sender_challenge.challengeID in sender_call_outs_challenges:
            ids_names_challenges.append(
                str(sender_challenge.challengeID.challengeID)+"---"+sender_challenge.challengeID.challengeName)

    context_dict["challenges"] = ids_names_challenges

    return JsonResponse(context_dict)


@login_required
def callout_description(request):
    ''' Return a full detail about the request callout'''

    def get_details(call_out, sender_score, is_sent_call_out, s_id, context_dict):
        ''' Get individual or class details'''

        # if the call out is individual then get participant avatar, score and submit time if there is any
        if call_out.isIndividual:
            call_out_participant = CalloutParticipants.objects.get(
                calloutID=call_out, courseID=current_course)

            context_dict['participant_avatar'] = StudentRegisteredCourses.objects.get(
                studentID=call_out_participant.participantID, courseID=current_course).avatarImage
            context_dict['call_out_participant'] = call_out_participant

            # initial message
            message = "This is an individual call out. "

            if not call_out.hasEnded:
                if is_sent_call_out:
                    message += "The participant will have to perform the same or better than you to win. Please see call out details bellow. "
                else:
                    message += "You will have to perform the same or better than the call out sender to win. Please see call out details bellow. "

            # try to get participant challenge
            try:
                participant_call_out_stat = CalloutStats.objects.get(
                    studentID=call_out_participant.participantID, calloutID=call_out, studentChallenge__challengeID=call_out.challengeID, courseID=current_course)
                context_dict['participant_score'] = participant_call_out_stat.studentChallenge.testScore
                context_dict['submit_time'] = participant_call_out_stat.submitTime
                context_dict['submission_status'] = True
                if call_out_participant.hasWon:
                    if sender_score == participant_call_out_stat.studentChallenge.testScore:
                        if is_sent_call_out:
                            message += "The participant of this call out has performed the same as you did. Congratulation! keep up the good work. "
                        else:
                            message += "You have performed the same as the call out sender did. Congratulation! keep up the good work. "
                    else:
                        if is_sent_call_out:
                            message += "The participant of this call out has performed better than you did. "
                        else:
                            message += "You have performed better than the call out sender did. Congratulation! keep up the good work. "
                    if participant_call_out_stat.calloutVC > 0:
                        if is_sent_call_out:
                            message += "Both you and participant have earned an amount of " + \
                                str(participant_call_out_stat.calloutVC) + \
                                " virtual currency for participating in this call out. "
                        else:
                            message += "Both you and sender have earned an amount of " + \
                                str(participant_call_out_stat.calloutVC) + \
                                " virtual currency for participation in this call out. "
                else:

                    if is_sent_call_out:
                        message += "The participant of this call out has failed to performed the same as you did or better and the call out has ended. "
                    else:
                        message += "You have failed to performed the same as the call out sender did or better and the call out has ended. "
                    if participant_call_out_stat.calloutVC > 0:
                        if is_sent_call_out:
                            message += "You have earned an amount of " + \
                                str(participant_call_out_stat.calloutVC) + \
                                " virtual currency."
                    if is_sent_call_out:
                        message += "Congratulation! keep up the good work. "

            except:

                if call_out_participant.hasSubmitted:
                    context_dict['submission_status'] = True
                else:
                    context_dict['submission_status'] = False
                context_dict['participant_score'] = "-"
                context_dict['submit_time'] = "-"
                if is_sent_call_out and call_out.hasEnded:
                    message += "The participant of this call out has failed to submit the call out on time. The call out has ended and is now closed. "
                elif is_sent_call_out:
                    message += "The participant of this call out has not submitted yet and the call out is still in progress. "
                elif call_out.hasEnded:
                    message += "You have fail to submit the call out on time. The call out has ended and is now closed. "

                else:
                    message += "You have not submitted yet and the call out is still in progress. "

            context_dict['message'] = message

        # else get class details such student avatars, scores and submit times
        else:
            call_out_participant_objects = CalloutParticipants.objects.filter(
                calloutID=call_out, courseID=current_course).order_by('?').exclude(participantID__user__id=s_id)

            # initial message
            message = "This is a class call out. "
            award_message = ""

            if not is_sent_call_out:
                call_out_part = CalloutParticipants.objects.get(
                    calloutID=call_out, participantID__user__id=s_id, courseID=current_course)

                if not call_out_part.hasSubmitted and not call_out.hasEnded:
                    message += "You will have to perform the same or better than the call out sender to win. Please see call out details bellow. "

                context_dict['participant_avatar'] = StudentRegisteredCourses.objects.get(
                    studentID=call_out_part.participantID, courseID=current_course).avatarImage
                context_dict['call_out_participant'] = call_out_part

                try:
                    participant_call_out_stat = CalloutStats.objects.get(
                        studentID=call_out_part.participantID, studentChallenge__challengeID=call_out.challengeID, calloutID=call_out, courseID=current_course)
                    context_dict['participant_score'] = participant_call_out_stat.studentChallenge.testScore
                    context_dict['submit_time'] = participant_call_out_stat.submitTime
                    context_dict['submission_status'] = True
                    if call_out_part.hasWon:
                        if sender_score == participant_call_out_stat.studentChallenge.testScore:
                            if participant_call_out_stat.calloutVC > 0:
                                message += "You have performed the same as the call out sender did. Both you and sender have earned an amount of " + str(
                                    participant_call_out_stat.calloutVC)+" virtual currency for participanting in this call out. Congratulation! keep up the good work. "
                            else:
                                message += \
                                    "You have performed the same as the call out sender did. Congratulation! keep up the good work. "
                        else:
                            if participant_call_out_stat.calloutVC > 0:
                                message += "You have performed better than the call out sender did. Both you and sender have earned an amount of " + str(
                                    participant_call_out_stat.calloutVC)+" virtual currency for participanting in this call out. Congratulation! keep up the good work. "
                            else:
                                message += \
                                    "You have performed better than the call out sender did. Congratulation! keep up the good work. "
                    else:
                        message += \
                            "You have failed to performed the same as the call out sender did or better. The call out has ended and is now closed. "
                except:
                    if call_out.hasEnded:
                        message += "You have failed to submit the call out on time. The call out has ended and is now closed. "
                    else:
                        message += "You have not submitted yet and the call out is still in progress. "
                    context_dict['participant_score'] = "-"
                    context_dict['submit_time'] = "-"
                    if call_out_part.hasSubmitted:
                        context_dict['submission_status'] = True
                    else:
                        context_dict['submission_status'] = False
            else:
                message += "The participants will have to perform the same or better than you to win. "

            participant_avatars = []
            call_out_participants = []
            submit_times = []
            participant_scores = []
            submission_status = []
            winning_status = []

            for call_out_participant in call_out_participant_objects:
                participant_avatars.append(StudentRegisteredCourses.objects.get(
                    studentID=call_out_participant.participantID, courseID=current_course).avatarImage)
                call_out_participants.append(call_out_participant)

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
                    if is_sent_call_out:
                        award_message = "You have earned an amount of " + \
                            str(participant_call_out_stat.calloutVC) + \
                            " virtual currency for participating in this call out. Congratulation! keep up the good work. "

                except:
                    participant_scores.append("-")
                    submit_times.append("-")
                    if call_out_participant.hasSubmitted:
                        submission_status.append(True)
                    else:
                        submission_status.append(False)

            if is_sent_call_out:
                if call_out.hasEnded:
                    message += award_message + "The call out has ended and is now closed. "
                message += "Please see call out details bellow. "

            context_dict['message'] = message

            context_dict['class_call_outs'] = zip(
                participant_avatars, call_out_participants, submit_times, participant_scores, submission_status, winning_status)

        return context_dict

    context_dict, current_course = studentInitialContextDict(request)
    student_id = context_dict['student']
    context_dict['isWarmup'] = True

    # get the needed detail, sent or requested call out

    if 'is_sent_call_out' in request.GET:
        is_sent_call_out = True
    else:
        is_sent_call_out = False

    context_dict['is_sent_call_out'] = is_sent_call_out

    if is_sent_call_out:
        call_out_id = request.GET['call_out_id']
        call_out = Callouts.objects.get(
            calloutID=call_out_id, courseID=current_course)
        context_dict['call_out'] = call_out

        if (call_out.endTime + timedelta(seconds=5)) <= timezone.now(): # TODO: Use current localtime and convert datetime to local
            try:
                call_out.hasEnded = True
                call_out.save()
            except:
                print("error")

        # get the remaing time before the call out is expired in seconds
        context_dict['time_left'] = (
            call_out.endTime - timezone.now()).total_seconds() # TODO: Use current localtime and convert datetime to local

        # get sender pure challenge higest score without curve and adjustment, and also call out virtual currency
        sender_call_out_stat = CalloutStats.objects.get(
            studentID=student_id, calloutID=call_out, courseID=current_course)
        sender_score = sender_call_out_stat.studentChallenge.testScore
        context_dict['sender_score'] = sender_score
        context_dict['test_score'] = sender_call_out_stat.studentChallenge.challengeID.totalScore
        context_dict['call_out_vc'] = sender_call_out_stat.calloutVC
        context_dict['sender_avatar'] = StudentRegisteredCourses.objects.get(
            studentID=call_out.sender, courseID=current_course).avatarImage

        context_dict = get_details(
            call_out, sender_score, is_sent_call_out, student_id.user.id, context_dict)

    else:

        call_out_participant_id = request.GET['call_out_participant_id']
        participant_id = request.GET['participant_id']
        call_out_participant = CalloutParticipants.objects.get(
            id=call_out_participant_id, participantID__user__id=participant_id, courseID=current_course)
        context_dict['call_out_participant'] = call_out_participant

        context_dict['participant_avatar'] = StudentRegisteredCourses.objects.get(
            studentID__user__id=participant_id, courseID=current_course).avatarImage
        call_out = call_out_participant.calloutID

        if (call_out.endTime + timedelta(seconds=5)) <= timezone.now(): # TODO: Use current localtime and convert datetime to local
            try:
                call_out.hasEnded = True
                call_out.save()
            except:
                print("error")
                
        context_dict['call_out'] = call_out
        call_out_stat = CalloutStats.objects.get(
            calloutID=call_out, studentID=call_out.sender, courseID=current_course)
        sender_score = call_out_stat.studentChallenge.testScore
        context_dict['sender_score'] = sender_score
        context_dict['test_score'] = call_out_stat.studentChallenge.challengeID.totalScore
        context_dict['call_out_vc'] = call_out_stat.calloutVC
        context_dict['sender_avatar'] = StudentRegisteredCourses.objects.get(
            studentID=call_out.sender, courseID=current_course).avatarImage

        # get the remaing time before the call out is expired in seconds
        context_dict['time_left'] = (
            call_out.endTime - timezone.now()).total_seconds() # TODO: Use current localtime and convert datetime to local

        context_dict = get_details(
            call_out, sender_score, is_sent_call_out, participant_id, context_dict)

    return render(request, 'Students/CalloutDescriptionForm.html', context_dict)


def call_out_list(student_id, current_course):
    '''Get student's call outs both sent and requested call outs'''

    # Callouts.objects.all().delete()

    # Get call outs that the student has sent
    call_outs = Callouts.objects.filter(
        sender=student_id, courseID=current_course)

    sent_call_outs = []
    sent_avatars_or_whole_class = []
    sent_times_left = []
    sent_call_out_topics = []
    for sent_call_out in call_outs:
        sent_call_outs.append(sent_call_out)
        # if it is individual, extract the participant's avatar url
        if sent_call_out.isIndividual:
            call_out_participant = CalloutParticipants.objects.get(
                calloutID=sent_call_out, courseID=current_course)
            sent_avatars_or_whole_class.append(StudentRegisteredCourses.objects.get(
                studentID=call_out_participant.participantID, courseID=current_course).avatarImage)
        # else append a string statig this is for the whole class
        else:
            sent_avatars_or_whole_class.append("Whole Class")
        time_left = (sent_call_out.endTime - timezone.now()).total_seconds() / 60.0 # TODO: Use current localtime and convert datetime to local

        sent_times_left.append(time_left)

        chall_topics = ChallengesTopics.objects.filter(
            challengeID=sent_call_out.challengeID)
        topic_names = ""
        for chall_topic in chall_topics:
            topic_names += chall_topic.topicID.topicName + "   "
        sent_call_out_topics.append(topic_names)

    # Get requested call outs
    call_out_participants = CalloutParticipants.objects.filter(
        participantID=student_id, courseID=current_course)

    requested_call_outs = []
    requested_times_left = []
    sender_avatars = []
    requested_call_out_topics = []
    for call_out_participant in call_out_participants:
        requested_call_outs.append(call_out_participant)
        time_left = (call_out_participant.calloutID.endTime -
                     timezone.now()).total_seconds() / 60.0 # TODO: Use current localtime and convert datetime to local

        requested_times_left.append(time_left)
        sender_avatars.append(StudentRegisteredCourses.objects.get(
            studentID=call_out_participant.calloutID.sender, courseID=current_course).avatarImage)

        chall_topics = ChallengesTopics.objects.filter(
            challengeID=call_out_participant.calloutID.challengeID)
        topic_names = ""
        for chall_topic in chall_topics:
            topic_names += chall_topic.topicID.topicName + "   "
        requested_call_out_topics.append(topic_names)

    return zip(sent_call_outs, sent_times_left, sent_avatars_or_whole_class, sent_call_out_topics), zip(requested_call_outs, requested_times_left, sender_avatars, requested_call_out_topics)
